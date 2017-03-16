# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    comodato = fields.Boolean(string='Comodato')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.comodato:
            res['valor_comodato'] = self.price_subtotal
            res['price_unit'] = 0.0
        return res