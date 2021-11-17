# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Course(models.Model):
    _name = "openacademy.course"
    _description = "OpenAcademy Courses"

    name = fields.Char(string=_("Title"), required=True, translate=True)
    description = fields.Text(string="Description")
    responsible_id = fields.Many2one('res.users', string="Responsible", ondelete='set null')
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions", )
    image = fields.Binary("Image", attachment=True)

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', _(u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)