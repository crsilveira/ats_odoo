 #-*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def write(self, vals):
        comodato = False
        date_order = False
        novos_valores = self.verifica(vals)

        if novos_valores['order_line']:
            for line in vals['order_line']:
                if line[2]:
                    for obj in line[2]:
                        if obj == 'comodato' and not comodato:
                            comodato=line[2]['comodato']
        else:
            for line in self.order_line:
                if line.comodato:
                    comodato=True
        if comodato:
            if novos_valores['valor_comodato']:
                if not vals['valor_comodato']:
                    raise UserError('Por favor, preencha o valor comodato')
            elif not self.valor_comodato:
                raise UserError('Por favor, preencha o valor comodato')


        if not novos_valores['date_order']:
            date_order = self.date_order
        else:
            date_order = novos_valores['date_order']
        if date_order:
            datetime_obj = datetime.strptime(date_order, '%Y-%m-%d %H:%M:%S')
        vals['validity_date'] = datetime.fromordinal(datetime_obj.toordinal()+15)

        return super(SaleOrder,self).write(vals)


    def verifica(self, vals):
        muda = {}
        muda['valor_comodato'] = False
        muda['date_order'] = False
        muda['order_line'] = False
        for record in vals:
            if not muda['valor_comodato']:
                if record == 'valor_comodato':
                    muda['valor_comodato'] = True
                else:
                    muda['valor_comodato'] = False
            if not muda['date_order']:
                if record == 'date_order':
                    muda['date_order'] = vals['date_order']
                else:
                    muda['date_order'] = False
            if not muda['order_line']:
                if record == 'order_line':
                    muda['order_line'] = True
                else:
                    muda['order_line'] = False
        return muda

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        #if self.invoice_type:
        #    res['invoice_type'] = self.invoice_type.id
        if self.divisao:
            res['divisao'] = self.divisao.id
        return res

    @api.multi
    @api.depends('order_line_serv.price_unit', 'order_line_serv.product_uom_qty')
    def _compute_service_total(self):
        total = 0.0
        for order in self:
            for line in order.order_line_serv:
                total += line.price_unit*line.product_uom_qty
        self.service_total = total
    
    order_line_serv = fields.One2many(
        'sale.order.line.serv', 'order_serv_id', 'Order Lines', 
        readonly=True, 
        states={
            'draft': [('readonly', False)], 
            'sent': [('readonly', False)]}, copy=True)
    service_total = fields.Float(
        compute='_compute_service_total', 
        digits=dp.get_precision('Account'), 
        readonly=True, store=True)
    divisao = fields.Many2one(
        'company.type', 
        string="Divisão", 
        index=True,
        domain="[('company_id','=',company_id)]"
    )
    recurring_next_date = fields.Date(string="Primeiro vencimento da mensalidade")
    ctr_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Dia Vencimento')
    ctr_payment_mode_id = fields.Many2one(
        'payment.mode', string="Modo de pagamento")
    valor_comodato = fields.Float(string="Valor do comodato")

    @api.depends('order_line.price_total', 'order_line.valor_desconto')
    def _amount_all(self):
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


    @api.multi
    @api.onchange('valor_comodato')
    def valor_comodato_change(self):
        vals = []
        product = self.env['product.product'].search([('name', 'ilike', 'comodato')])
        for line in self.order_line_serv:
            if line.product_id.id == product.id:
                line.price_unit = self.valor_comodato
                return
            else:
                vals.append((0,0,{
                    'product_id' : line.product_id,
                    'price_unit' : line.price_unit,
                    'product_uom_qty' : line.product_uom_qty,
                    'product_uom' : line.product_uom
                }))
        if self.valor_comodato != 0.0:
            vals.append((0,0,{
                'product_id': product.id,
                'price_unit': self.valor_comodato,
                'product_uom_qty': 1,
                'product_uom': 1
            }))
            #res = self.order_line_serv.create(vals)
            self.order_line_serv = vals


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
