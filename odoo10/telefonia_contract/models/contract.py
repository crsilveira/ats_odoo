# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.model
    def create(self, vals):
        contract_id = super(AccountAnalyticAccount,self).create(vals)
        if 'recurring_invoice_line_ids' in vals:
            for x in vals.get('recurring_invoice_line_ids'):
                if 'product_id' in x[2]:
                    prod = self.env['product.template'].browse([x[2].get('product_id')])
                    prod.write({'contract_id': contract_id.id})
        return contract_id

    @api.multi
    def write(self, values):
        res = super(AccountAnalyticAccount, self).write(values)
        if 'recurring_invoice_line_ids' in values:
            for x in values.get('recurring_invoice_line_ids') :
                if x[2] and 'product_id' in x[2]:
                    prod = self.env['product.template'].browse([x[2].get('product_id')])
                    prod.write({'contract_id': self.id})
        return res

