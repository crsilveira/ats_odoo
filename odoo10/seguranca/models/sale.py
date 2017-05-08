 #-*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.invoice_type:
            res['invoice_type'] = self.invoice_type.id
        if self.divisao:
            res['divisao'] = self.divisao.id
        return res
    # CRIAR CONTRATO AO CRIAR A NOTA FISCAL

    @api.multi
    @api.depends('order_line_serv.price_unit', 'order_line_serv.product_uom_qty')
    def _compute_service_total(self):
        total = 0.0
        for order in self:
            for line in order.order_line_serv:
                total += line.price_unit*line.product_uom_qty
        self.service_total = total
    
    order_line_serv = fields.One2many('sale.order.line.serv', 'order_serv_id', 'Order Lines', readonly=True, states={'draft': [('readonly',      False)], 'sent': [('readonly', False)]}, copy=True)
    service_total = fields.Float(compute='_compute_service_total', digits=dp.get_precision('Account'), readonly=True, store=True)
    invoice_type = fields.Many2one('account.invoice.type', string='Tipo do faturamento', index=True)
    divisao = fields.Many2one('company.type', string="Divisão", index=True)
    #service_total = fields.Float(digits=dp.get_precision('Account'), readonly=True)


    @api.depends('order_line.price_total', 'order_line.valor_desconto')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """

        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_total': amount_untaxed + amount_tax + self.service_total,
                'total_bruto': sum(l.valor_bruto
                                   for l in order.order_line) + self.service_total,
            })

class SaleOrderLineServ(models.Model):

    """
    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False 
    """
    _name = 'sale.order.line.serv'
    _description = 'Sales Order Line Service'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id.id
            vals['product_uom_qty'] = 1.0

        self.update(vals)

        return {'domain': domain}

    order_serv_id = fields.Many2one('sale.order', 'Order Reference', required=True, ondelete='cascade', index=True, readonly=True)
    product_id = fields.Many2one('product.product', u'Serviço', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict')
    price_unit = fields.Float(u'Preço', required=True, digits= dp.get_precision('Product Price'))
    product_uom_qty = fields.Float('Quantity', digits= dp.get_precision('Product UoS'), required=True)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    discount = fields.Float('Discount (%)', digits= dp.get_precision('Discount'), readonly=True)

    _order = 'order_serv_id desc, id'
    _defaults = {
        'discount': 0.0,
        'product_uom_qty': 1,
        'price_unit': 0.0,
    }