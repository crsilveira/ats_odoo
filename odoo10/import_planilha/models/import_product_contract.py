# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64
import csv
from datetime import datetime, date
from cStringIO import StringIO
import tempfile
import time
import xlrd
import re

_TASK_STATE = [('open', 'Novo'),('done', 'Importado'), ('cancelled', 'Cancelado')]

class ImportProductContract(models.Model):
    _name = 'import.product.contract'

    name = fields.Char('Descrição', size=256, required=True, default='/')
    input_file = fields.Binary('Arquivo', required=False)
    contract_id = fields.Many2one('account.analytic.account', 'Contrato', required=True)
    user_id = fields.Many2one('res.users', string='Inserido por', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    header =  fields.Boolean('Header')
    state = fields.Selection([
        ('open', 'Novo'),
        ('done', 'Importado'),
        ('cancel', 'Cancelado'),
        ], string='Situação', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')

    @api.multi
    def set_done(self):
        return self.write({'stage': 'done'})
        
    @api.multi
    def set_open(self):
        return self.write({'stage': 'open'})

    @api.multi
    def set_cancelled(self):
        return self.write({'stage': 'cancelled'})

    @api.multi
    def import_to_db(self):
        prod_id = 0
        prod_obj = self.env['product.product']
        ctr = self.env['account.analytic.account'].browse([self.contract_id.id])
        ctr_line = self.env['account.analytic.invoice.line']
        for chain in self:
            file_path = tempfile.gettempdir()+'/file.xls'
            data = chain.input_file
            f = open(file_path,'wb')
            f.write(data.decode('base64'))
            f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            conta_registros = 0
            for rownum in range(first_sheet.nrows):
                rowValues = first_sheet.row_values(rownum)
                if rownum > 0:
                    vals = {}
                    simcard = ''
                    if rowValues[3]:
                        simcard = rowValues[3]
                    vlr = 0.0
                    if rowValues[8]:
                        vlr = rowValues[8]
                    p_id = prod_obj.search([('default_code','=',simcard),('contract_id','=',False)])
                    if not p_id:
                        continue
                    l_id = ctr_line.search([('analytic_account_id','=',self.contract_id.id),('product_id','=',p_id.id)])
                    if not l_id:
                        vals['recurring_invoice_line_ids'] = [
                            (0, 0,
                            {
                                'name': simcard,
                                'product_id': p_id.id,
                                'quantity': 1.0,
                                'price_unit': vlr ,
                                'uom_id': p_id.uom_id.id
                            }
                             )
                        ]
                        ctr.write(vals)
                        conta_registros += 1
            print 'TOTAL DE REGISTROS INCLUIDOS : %s' %(str(conta_registros))

        return self.write({'state':'done'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
