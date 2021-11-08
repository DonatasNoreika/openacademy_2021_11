# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Course(models.Model):
    _name = "openacademy.course"
    _description = "OpenAcademy Courses"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    responsible_id = fields.Many2one('res.users', string="Responsible", ondelete='set null')
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions", )