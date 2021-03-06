# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import timedelta

class Session(models.Model):
    _name = "openacademy.session"
    _description = "OpenAcademy Sessions"

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date(string="End Date", store=True,
                           compute='_get_end_date', inverse='_set_end_date')
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    taken_seats = fields.Float(string="Taken seats (%)", compute='_taken_seats')

    instructor_id = fields.Many2one('res.partner', string="Instructor", ondelete='set null',
                                    domain=['|', ('instructor', '=', True), ('category_id.name', 'ilike', 'Teacher')])
    course_id = fields.Many2one('openacademy.course', string="Course", ondelete='set null')
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)
    active = fields.Boolean(default=True)
    color = fields.Integer()
    image = fields.Binary("Image", attachment=True)

    status = fields.Selection([
        ('draft', "Draft"),
        ('started', "Started"),
        ('done', "Done"),
        ('cancelled', "Cancelled"),
    ], string="Progress", default='draft', translate=True)


    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for record in self:
            if not record.seats:
                record.taken_seats = 0.0
            else:
                record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': f"Incorrect 'seats' value",
                    'message': f"The number of available seats may not be negative: {self.seats}",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1

    def send_session_report(self):
        # Find the e-mail template
        template = self.env.ref('openacademy.openacademy_session_mail_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('send_mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)