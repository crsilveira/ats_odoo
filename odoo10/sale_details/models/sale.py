# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _track = {
        'state': {
            'sale.mt_order_sent': lambda self, cr, uid, obj, ctx=None: obj.state in ['sent']
        },
    }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    data_servico = fields.Date('Data Serviço')
    hora_inicio = fields.Float('Inicio')
    hora_fim = fields.Float('Fim')

    @api.multi
    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

    @api.onchange('data_servico', 'hora_inicio', 'hora_fim')
    def completar_servico(self):
        #import pudb;pu.db
        servico = ''
        if self.data_servico:
            data_s = self.data_servico[8:11] + '/' + self.data_servico[5:7] + '/' + self.data_servico[0:4]
            servico = self.product_id.name + ' (' + data_s
        if self.hora_inicio:
            hour, minute = self.float_time_convert(self.hora_inicio)
            min = str(minute)
            if minute < 10:
                min = '0%s' %(str(minute))
            servico = servico + ' - ' + str(hour) + ':' + min
        if self.hora_fim:
            hour, minute = self.float_time_convert(self.hora_fim)
            min = str(minute)
            if minute < 10:
                min = '0%s' %(str(minute))
            servico = servico + ' - ' + str(hour) + ':' + min + ')'

        if servico:
            self.name = servico
        #result = super(SaleOrderLine, self).create(vals)


        #        return result

    """
    @api.multi
    def write(self, vals):
        #    return super(SaleOrder, self).write(vals)
    """