# -*- coding: utf-8 -*-

import datetime
from odoo import _,fields, api, models
from odoo.exceptions import UserError

class EventEvent(models.Model):
    _inherit = "event.event"

    product_id = fields.Many2one('product.product', string='Produto', index=True)
    qty = fields.Float(string='Duração em horas')

    @api.onchange('product_id')
    def _onchange_id(self):
        evento = self.env['event.event'].search([('id', '!=', False)])
        if any((((line.date_end > self.date_begin and line.date_begin < self.date_begin) or (
                line.date_end > self.date_end and line.date_begin < self.date_end) or (
                line.date_end < self.date_end and line.date_begin > self.date_begin)) and line.id != self.id) and line.product_id.id == self.product_id.id
               for
               line in evento):
            raise UserError('Existe um evento ocorrendo neste horário')

        else:
            self.name = self.product_id.name
            self.name

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        if self.date_end:
            self.qty = self.set_duration()

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_begin:
            self.qty = self.set_duration()

    def set_duration(self):
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d %H:%M:%S')
        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d %H:%M:%S')
        dur = date_end - date_begin
        duration = dur.days * 24
        duration += float(dur.seconds)/3600
        return duration

    @api.multi
    def write(self, vals):
        evento = self.env['event.event'].search([('id', '!=', False)])
        if any((((line.date_end > self.date_begin and line.date_begin < self.date_begin) or (line.date_end > self.date_end and line.date_begin < self.date_end ) or (line.date_end < self.date_end and line.date_begin > self.date_begin)) and line.id != self.id) and line.product_id.id == self.product_id.id for
               line in evento):
            raise UserError('Existe um evento ocorrendo neste horário')
        else:
            vals['qty'] = self.set_duration()
            res = super(EventEvent, self).write(vals)
        return res

    @api.one
    def button_confirm(self):
        self.state = 'confirm'
        venda = self.env['sale.order']
        vals = {}
        vals['partner_id'] = self.address_id.id
        vals['company_id'] = self.company_id.id
        order_line = []
        order_line.append((0, 0, {
            'product_id': self.product_id.id,
             #'price_unit': 1,
            'product_uom_qty': self.qty,
            'name': self.product_id.name,
            'uom_id': 1
        }))
        vals['order_line'] = order_line
        venda.create(vals)


