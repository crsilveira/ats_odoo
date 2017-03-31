# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    valor_comodato = fields.Float(string="Valor Comodato")