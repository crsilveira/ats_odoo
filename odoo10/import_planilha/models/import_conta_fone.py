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

_TASK_STATE = [('open', 'Novo'),('done', 'Importado'), ('cancelled', 'Cancelado')]

class ImportConta(models.Model):
    _name = 'import.conta'
    
    name = fields.Char('Descrição', size=256, required=True)
    input_file = fields.Binary('Arquivo', required=False)
    user_id = fields.Many2one('res.users', 'Inserido por', track_visibility='onchange')
    header =  fields.Boolean('Header')
    state = fields.Selection(_TASK_STATE, 'Situacao', required=True,)

    _defaults = {
        'state': 'open',
        'user_id': lambda obj, cr, uid, context: uid,
        'name':'/',
    }

    @api.multi
    def set_done(self):
        return self.write({'stage': 'done'})
        
    def set_open(self):
        return self.write({'stage': 'open'})

    def set_cancelled(self):
        return self.write({'stage': 'cancelled'})

    def import_to_xls(self):
        client_id = 0
        client_obj = self.env['res.partner']
        context['result_ids'] = []
        for chain in self:
            file_path = tempfile.gettempdir()+'/file.xls'
            data = chain.input_file
            f = open(file_path,'wb')
            f.write(data.decode('base64'))
            f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            cnpj_jafoi = ''
            parent_id = 0
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                #import pudb;pudb.set_trace()
                if rownum > 0 and rownum < 50:
                    cnpj_cpf = rowValues[2]  
                    if cnpj_cpf == '000.000.000-00':
                        cnpj_cpf = ''

                    # Pulando CNPJ Repetidos ##########  PARA INSERIR OS CONTATOS COMENTE AS 2 LINHAS ABAIXO
                    if cnpj_jafoi == cnpj_cpf:
                        continue

                    if cnpj_cpf == '':
                        cnpj_jafoi = 'Diferente'
                    codigo = rowValues[0]
                    nome = u'%s' %(rowValues[4])
                    #+ '-' + str(rowValues[14]) + '-' + str(rowValues[15])
                    ie = rowValues[3]  
                    endereco = rowValues[6]  
                    numero = rowValues[7]  
                    bairro = rowValues[8]  
                    cidade = rowValues[9]
                    # buscar o codigo da cidade
                    uf = rowValues[10]
                    # buscar o estado
                    complemento = rowValues[18]
                    cep = rowValues[11]
                    fone = rowValues[12]
                    fone1 = rowValues[13]
                    email = rowValues[17]
                    aniversario = rowValues[19]
                    data_cadastro = rowValues[5]
                    empresa = False
                    if len(cnpj_cpf) > 14:
                        empresa = True
                    # verificando se o cnpj ja esta cadastrado
                    sql_req= """
                        SELECT p.id, p.ref
                        FROM res_partner p
                        WHERE
                        (p.cnpj_cpf = '%s')
                        or (p.name = '%s')
                        """ % (cnpj_cpf, nome)
                    cr.execute(sql_req)
                    sql_cnpj = cr.dictfetchone()
                    if sql_cnpj:
                        parent_id = sql_cnpj['id']

                    cnpj_jafoi = cnpj_cpf
                    if parent_id != 0:
                        # limpo o cnpj pois, ja tem na empresa principal
                        cnpj_cpf = '' 
                        if codigo == sql_cnpj['ref']:
                            continue # estou inserindo o contato

                    if parent_id != 0 and int(codigo) == int(float(sql_cnpj['ref'])):
                        continue

                    print " codigo: %s , nome : %s " %(codigo, rowValues[0])
                    # buscando a cidade
                    sql_req= """
                        SELECT p.id, p.name
                        FROM l10n_br_base_city p
                        WHERE
                        (UPPER(p.name) like '%s')
                        """ % (cidade)
                    cr.execute(sql_req)
                    sql_res = cr.dictfetchone()
                    if not sql_res:
                        raise osv.except_osv(u'Erro importação',u'CIDADA NÃO ENCONTRADA : %s' %(cidade))

                    if sql_res:
                        if uf == 'SP':
                            state = 79
                        elif uf == 'MG':
                            state = 76
                        elif uf == 'RJ':
                            state = 78
                        elif uf == 'PR':
                            state = 80
                        elif uf == 'RS':
                            state = 82
                        #work = self.pool.get('project.task.work')
                        vals = {'name': nome,
                              'is_company': empresa,
                              'legal_name': nome,
                              'street': endereco,
                              'street2': complemento,
                              'date': data_cadastro,
                              'birthdate_date': aniversario,
                              'number': numero,
                              'district': bairro,
                              'country_id': 32,
                              'state_id': state,
                              'l10n_br_ciy_id': sql_res['id'],
                              'city': sql_res['name'],
                              'phone': fone,
                              'mobile': fone1,
                              'email': email,
                              'zip': cep,
                              'ref': codigo,
                            }
                        if parent_id > 0:
                            vals['parent_id'] = parent_id
                            
                        if cnpj_cpf != '':
                            vals['cnpj_cpf'] = cnpj_cpf
                        #import pudb;pudb.set_trace()
                        client_id =  client_obj.create(cr, uid, vals, context=None)
                        c_ids = client_obj.browse(cr, uid, [client_id], context=None)
                        if not c_ids.l10n_br_city_id:
                            city_obj = self.pool.get('l10n_br_base.city')
                            city_id = city_obj.search(cr, uid, [('name','=',sql_res['name'])], context=None)
                            if city_id:
                                client_obj.write(cr, uid, client_id, {'l10n_br_city_id': city_id[0]}, context=context)


        return client_id


    def import_to_db(self, cr, uid, ids, context={}):
        print 'aqui'

    '''    
    def import_to_db(self, cr, uid, ids, context={}):

        context['result_ids'] = []
        result_pool = self.pool.get('ea_import.chain.result')
        for chain in self.browse(cr, uid, ids, context=context):
            csv_reader=unicode_csv_reader(StringIO(base64.b64decode(chain.input_file)),delimiter=str(";"),quoting=(not
chain.delimiter and csv.QUOTE_NONE) or csv.QUOTE_MINIMAL,quotechar=chain.delimiter and str("'") or None, charset=chain.charset)

            strstate = 'normal'
            if chain.state == 'done':
               strstate = 'Importado'

            if chain.state == 'cancelled':
               strstate = 'Suspenso'

            strmsg = 'Situacao do arquivo : %s ' % (strstate,)
            if chain.state in ('done','cancelled'):
                raise osv.except_osv(strmsg,'Ative o novamente para poder importar.')

            #if chain.header:
            #    csv_reader.next()
            result_ids = {}

            #'student_id': fields.many2one('op.student',string='Student', required=True),
            #'session_id':fields.many2one('op.exam.session','Exam Session', required=True, select=True, readonly=True),
            #'avaliacao':fields.float('Avaliação'),
            #'falta':fields.float('Faltas')
            
            #apont_obj = self.pool.get('project.task.work')
            apont_obj = self.pool.get('op.exam')

            #return res
            primeira_linha = 0
            for row in csv_reader:
                if primeira_linha == 0:
                    primeira_linha = 1
                else:
                    if primeira_linha == 1:
                        sql_req= """
                            SELECT c.id, c.course_id, c.classroom_id 
                            FROM op_exam_session c
                            WHERE
                            (c.name = '%s')
                            """ % (row[0])

                        cr.execute(sql_req)
                        sql_res = cr.dictfetchone()

                        if sql_res:
                            session_id = sql_res['id']
                            course_id  = sql_res['course_id']
                            classroom_id  = sql_res['classroom_id']
                        if not sql_res:
                            strmsg = 'Exame : %s '
                            raise osv.except_osv(strmsg,' nao localizado no sistema.')
                        primeira_linha = 2
                
                    #csv_reader.next()
                    # for row in csv_reader:
                    if len(row)>0:
                        sql_usu= """
                            SELECT u.id, op.id as exam 
                            FROM op_exam op, op_student u
                            WHERE
                            (op.student_id = u.id)
                            AND 
                            (op.session_id = %s)
                            AND
                            (u.roll_number = '%s')
                            AND
                            (u.course_id = '%s')
                            AND 
                            (u.classroom_id = '%s')
                            """ % (session_id, row[2], course_id, classroom_id)
                        cr.execute(sql_usu)
                        sql_resusu = cr.dictfetchone()
               
                        #pdb.set_trace()
                        if sql_resusu:
                            user_id = sql_resusu['id']
                            exam_id = sql_resusu['exam']

                        else:
                            strmsg = 'Aluno : %s ' % (row[0],)
                            raise osv.except_osv(strmsg,'nao localizado o aluno com este numero.') 
                            user_id = 0
                    #work = self.pool.get('project.task.work')
                    vals = {'session_id': session_id,
                        'student_id': user_id,
                        'avaliacao': row[3],
                        'falta': row[4],
                    }
                    #apont_obj.create(cr, uid, vals, context)
                    apont_obj.write(cr, uid, exam_id, vals)


                #pdb.set_trace()
                #for [nada,nome,os,categoria] in csv_reader:
                #print 'nada=%s | nome=%s | os=%s | categoria=%s' %(nada,nome,os,categoria)

        #return True:w
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
    '''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
