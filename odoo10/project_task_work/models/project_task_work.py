# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    hours_in = fields.Float('Entrada')
    hours_out = fields.Float('Saída')

    @api.onchange('hours_in', 'hours_out')
    def compute_total(self):
        if self.hours_out < self.hours_in:
            self.unit_amount = (24.0-self.hours_in)+self.hours_out
        else:
            self.unit_amount = self.hours_out - self.hours_in