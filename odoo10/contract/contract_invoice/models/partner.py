# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_mode_id = fields.Many2one(
        'payment.mode',
        string='Payment Mode'
        )