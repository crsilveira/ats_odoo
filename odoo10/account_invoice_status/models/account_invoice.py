# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    state = fields.Selection(selection_add=[
        ('protesto', 'Protesto'),
        ('suspenso', 'Suspenso'),
        ('renegociado', 'Renegociado'),
    ])

