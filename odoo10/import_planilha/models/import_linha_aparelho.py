# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Enapps LTD (<http://www.enapps.co.uk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
import base64
import csv
from datetime import datetime, date
from cStringIO import StringIO
import tempfile
import time
import xlrd
import re


class ImportLinhaAparelho(models.Model):
    _name = 'import.linha.aparelho'
    
    name = fields.Char('Descrição', size=256, required=True, default='/')
    input_file = fields.Binary('Arquivo', required=False)
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
        prod_obj = self.env['product.product']
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
                    fone = ''
                    if rowValues[1]:
                        fone = rowValues[1]
                    simcard = ''
                    if rowValues[3]:
                        simcard = rowValues[3]
                    plano = ''
                    if rowValues[4]:
                        plano = rowValues[4]
                    id_ordem = ''
                    if rowValues[5]:
                        id_ordem = rowValues[5]
                    nf = ''
                    if rowValues[6]:
                        nf = rowValues[6]
                    vlr = 0.0
                    if rowValues[8]:
                        vlr = rowValues[8]

                    p_id = prod_obj.search([('default_code','=',simcard)])

                    if p_id:
                        continue
                    desc = 'Plano - %s, Ordem - %s, NF - %s' %(plano, id_ordem, nf)
                    vals = {'name': fone,
                        'default_code': simcard,
                        'description': desc,
                        'type': 'service',
                        'mobile': True,
                        'list_price':vlr
                        }
                    print vals
                    p_id =  prod_obj.create(vals)
                    conta_registros += 1
            print 'TOTAL DE REGISTROS INCLUIDOS : %s' %(str(conta_registros))
                    #if conta_registros in (50,150,200,250,300,350,400,450,500,600,700,800,900,1000,1100,1200,1300,1400,1500):
                    #    cr.commit()

        return self.write({'state':'done'})
