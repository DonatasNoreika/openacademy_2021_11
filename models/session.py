# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class Session(models.Model):
    _name = "openacademy.session"
    _description = "OpenAcademy Sessions"

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    taken_seats = fields.Float(string="Taken seats (%)", compute='_taken_seats')

    instructor_id = fields.Many2one('res.partner', string="Instructor", ondelete='set null',
                                    domain=['|', ('instructor', '=', True), ('category_id.name', 'ilike', 'Teacher')])
    course_id = fields.Many2one('openacademy.course', string="Course", ondelete='set null')
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    active = fields.Boolean(default=True)

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