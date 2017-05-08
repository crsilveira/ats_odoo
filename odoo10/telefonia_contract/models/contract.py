# -*- coding: utf-8 -*-
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.one
    @api.depends('recurring_invoice_line_ids.price_unit',
                 'recurring_invoice_line_ids.quantity')
    def _total_contrato(self):
        lines = self.recurring_invoice_line_ids
        self.valor_total = sum((l.price_unit*l.quantity) for l in lines)

    valor_total = fields.Float(
        string='Valor Total', readonly=True, compute='_total_contrato',
        digits=dp.get_precision('Account'), store=True)

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

