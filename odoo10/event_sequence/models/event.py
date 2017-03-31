# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta


class EventEvent(models.Model):
    """Event"""
    _inherit = 'event.event'

    descricao = fields.Text(
        string='Descricao Curso')
    default_code = fields.Char(
        default='/'
        )

    """
    _sql_constraints = [
        ('uniq_default_code',
         'unique(default_code)',
         'Já existe curso com este código'),
        ]
    """

    @api.model
    def create(self, vals):
        if 'default_code' not in vals or vals['default_code'] == '/':
            sequence = self.env.ref('event_sequence.seq_event')
            vals['default_code'] = sequence.next_by_id()
        return super(EventEvent, self).create(vals)

    @api.multi
    def write(self, vals):
        for event in self:
            if event.default_code in [False, '/']:
                sequence = self.env.ref('event_sequence.seq_event')
                vals['default_code'] = sequence.next_by_id()
            super(EventEvent, event).write(vals)
        return True

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.default_code:
            default.update({
                'default_code': self.default_code + _('-copy'),
            })
        return super(EventEvent, self).copy(default)

