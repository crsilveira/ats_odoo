# -*- coding: utf-8 -*-
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('recurring_invoice_line_ids.price_subtotal')
    def _amount_total(self):
        soma = 0.0
        for line in self.recurring_invoice_line_ids:
            soma += (line.price_subtotal)
        self.amount_total = soma

    payment_mode_id = fields.Many2one(
        'payment.mode',
        string='Payment Mode'
        )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Dia Vencimento'
        )
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position',
        string='Fiscal Position'
        )
    invoice_partner_id = fields.Many2one('res.partner', string='Cliente faturamento')


    amount_total = fields.Float(compute='_amount_total', string="Valor total", digits=dp.get_precision('Product Price'), store=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.payment_mode_id:
            self.payment_mode_id = self.partner_id.payment_mode_id.id
        if self.partner_id and self.partner_id.property_payment_term_id:
            self.payment_term_id = self.partner_id.property_payment_term_id.id
        if self.partner_id and self.partner_id.property_account_position_id:
            self.fiscal_position_id = self.partner_id.property_account_position_id.id
        if self.partner_id:
            if self.partner_id.legal_name:
                self.name = self.partner_id.legal_name
            else:
                self.name = self.partner_id.name

    @api.model
    def _prepare_invoice(self):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice()
        if self.payment_mode_id:
            invoice_vals['payment_mode_id'] = self.payment_mode_id.id
            #invoice_vals['partner_bank_id'] = (
            #    contract.partner_id.bank_ids[:1].id or
            #    contract.payment_mode_id.bank_id.id)
        if self.payment_term_id:
            invoice_vals['payment_term_id'] = self.payment_term_id.id
        if self.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id

        return invoice_vals


    @api.multi
    def write(self, values):
        vals = {}
        if 'payment_term_id' in values:
            vals['property_payment_term_id'] = values.get('payment_term_id')
        if 'payment_mode_id' in values:
            vals['payment_mode_id'] = values.get('payment_mode_id')
        if 'fiscal_position_id' in values:
            vals['property_account_position_id'] = values.get('fiscal_position_id')
        if vals:
            partner = self.env['res.partner'].browse([self.partner_id.id])
            partner.write(vals)
        return super(AccountAnalyticAccount, self).write(values);


    @api.model
    def create(self, values):
        vals = {}
        if 'payment_term_id' in values:
            vals['property_payment_term_id'] = values.get('payment_term_id')
        if 'payment_mode_id' in values:
            vals['payment_mode_id'] = values.get('payment_mode_id')
        if 'fiscal_position_id' in values:
            vals['property_account_position_id'] = values.get('fiscal_position_id')
        if vals:
            partner = self.env['res.partner'].browse([values.get('partner_id')])
            partner.write(vals)
        return super(AccountAnalyticAccount, self).create(values);