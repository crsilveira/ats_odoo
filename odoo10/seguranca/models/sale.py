 #-*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # CRIAR CONTRATO AO CRIAR A NOTA FISCAL
    """
    @api.model
    def _prepare_invoice(self, order, lines):
        result = super(SaleOrder, self)._prepare_invoice(order, lines)

        # criar o CONTRATO

        contract_id = env['account.analytic.account'].create({
            'name': order.partner_id.name,
            'partner_id': order.partner_id,
            'manager_id': order.user_id.id,
            'company_id': order.company_id.id,
            'code': order.id,
            'payment_mode_id': order.payment_mode_id.id,
            'payment_term_id': order.payment_term_id.id,
            'date_start': order.date_start,
            'recurring_interval': order.interval,
            'recurring_invoices': True,
            'recurring_next_date': order.date_next_invoice,
            'recurring_invoice_line_ids': lines,
            })
        return result
    """

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