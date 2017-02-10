# -*- coding: utf-8 -*-
# © 2017 Carlos Silveira, ATS Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import tempfile
import StringIO
import base64
import os

from datetime import datetime
from odoo import fields, models, _, api
#from febraban.fixed_files import Fixed_files
from odoo.addons.import_planilha.febraban.fixed_files import Fixed_files


from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ImportConta(models.Model):
    _inherit = 'mail.thread'
    _name = 'import.conta'
    
    name = fields.Char('Descrição', size=256, required=True)
    input_file = fields.Binary('Arquivo', required=False)
    user_id = fields.Many2one('res.users', string='Inserido por', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    header =  fields.Boolean('Header')
    state = fields.Selection([
        ('open', 'Novo'),
        ('done', 'Importado'),
        ('cancel', 'Cancelado'),
        ], string='Situação', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')
    data_vencimento = fields.Date('Data Vencimento')

    vendas_ids = []

    """@api.model
    def create(self, vals):
        self.vendas_ids = []
        return super(ImportConta, self).create(vals)
    """

    def set_done(self):
        return self.write({'state': 'done'})
        
    def set_open(self):
        return self.write({'state': 'open'})

    def set_cancelled(self):
        return self.write({'state': 'cancelled'})

    def confirma_vendas(self, vnd_ids):
        for vnd in vnd_ids:
            vnd.action_confirm()


    def cria_venda(self, emissao, fone, mes, valor_chamadas, valor_servico, valor_total, vencimento):
        msg_inc = []
        # localizo o produto
        pdt = self.env['product.product']
        pdt_ids = pdt.search([
            ('name','=', fone)
        ])
        if not pdt_ids:
            # nao tem esta linha no cadastro do produto
            msg_inc.append({'sem_linha': fone})

        #localizo o contrato do cliente
        ctr = self.env['account.analytic.invoice.line']
        ctr_ids = ctr.search([
            ('product_id', '=', pdt_ids.id)
        ])

        if not ctr_ids:
            # esta linha nao esta em nenhum contrato
            msg_inc.append({'sem_contrato': fone})

        """
        CONTRATOS INATIVOS ESTA PEGANDO ???
        if ctr_ids.analytic_account_id.state == :
            # esta linha nao esta em nenhum contrato
            msg_inc.append({'sem_contrato': fone})
        """
        if len(msg_inc):
            return msg_inc

        # criar o pedido de vendas
        pd = '%s-%s' %(ctr_ids.analytic_account_id.code or str(ctr_ids.analytic_account_id.id), vencimento)
        venda = self.env['sale.order']
        venda_ids = venda.search([
            ('partner_id','=',ctr_ids.analytic_account_id.partner_id.id),
            ('state', '=', 'draft'),
            ('name', '=', pd)
        ])
        if venda_ids:
            # procura se ja existe esta linha lancada
            for line in venda_ids.order_line:
                if pdt_ids.id == line.product_id.id:
                    return msg_inc
        order_line = []
        if valor_servico > 0:
            order_line.append(
                (0, 0,
                 {
                     'product_id': pdt_ids.id,
                     'product_uom_qty': 1,
                     'name': 'Consumo de Servicos',
                     'price_unit': valor_servico,
                 }
                 )
            )
        if valor_chamadas > 0:
            order_line.append(
                (0, 0,
                 {
                     'product_id': pdt_ids.id,
                     'product_uom_qty': 1,
                     'name': 'Consumo de Ligacoes',
                     'price_unit': valor_chamadas,
                 }
                 )
            )
        default_saleorder = {
                'order_line': order_line
            }
        if venda_ids:
            incluir = True
            for line in venda_ids.order_line:
                if line.product_id.id == pdt_ids.id:
                    incluir = False
            if incluir:
                v_ids = venda.browse([venda_ids.id])
                try:
                    v_ids.write(default_saleorder)
                except:
                    msg_inc.append({'erro_add': '%s-%s-%s' % (
                        ctr_ids.analytic_account_id.partner_id.name,
                        ctr_ids.analytic_account_id.code,
                        fone)})
                    print "2-adicionei na venda existente"
        else:
            try:
                vnd_id = venda.create(dict(
                    default_saleorder.items(),
                    name=pd,
                    partner_id=ctr_ids.analytic_account_id.partner_id.id,
                    user_id = ctr_ids.analytic_account_id.manager_id.id
                ))
                self.vendas_ids.append(vnd_id)
            except:
                msg_inc.append({'erro_inc': '%s-%s-%s' % (
                    ctr_ids.analytic_account_id.partner_id.name,
                    ctr_ids.analytic_account_id.code,
                    fone)})
            print "1-nao tem venda, inclui"
        #if len(msg_inc):
        #    self.message_post(body=_(msg_inc))

        return msg_inc

    def _parse_febraban(self, data_file, raise_error=False):
        cnab240_file = tempfile.NamedTemporaryFile()
        cnab240_file.write(data_file)
        cnab240_file.flush()
        #arquivo = Arquivo(claro, arquivo=open(, 'r'))
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'resumo.json')
        ff = Fixed_files(file_path, dic=False, checklength=False)
        records = open(cnab240_file.name).readlines()
        rec_in = []
        for record in records:
            # 10 RESUMO VALOR DAS LIGACOES E GASTOS SERVICOS
            # O QUE EU PRECISO PARA JOGAR NA FATURA
            if record[0] == '1':
                rec_in.append(ff.parse(record))

        msg_vnd = []
        for n, r in enumerate(rec_in):
            # print ff.unparse(r) == records[n]
            #print r.data_emissao
            #print r.identificador_recurso
            #print r.mes_referencia
            #print r.numero_recurso
            #print r.valor_total_registros
            #print r.valos_total_servicos
            #print r.valor_total_geral
            #print r.data_vencimento
            vlt = 0.00
            vlr = 0.00
            vls = 0.00
            if r.valor_total_geral > 0:
                vlt = float(r.valor_total_geral)/100
            if r.valor_total_registros > 0:
                vlr = float(r.valor_total_registros)/100
            if r.valos_total_servicos > 0:
                vls = float(r.valos_total_servicos)/100
            if vlt > 0.00:
                msg_vnd.append(self.cria_venda(r.data_emissao
                       ,r.numero_recurso.strip()
                       ,r.mes_referencia
                       ,vlr
                       ,vls
                       ,vlt
                       ,r.data_vencimento
                ))
            #self.data_vencimento = r.data_vencimento

        if len(msg_vnd):
            msg = ''
            for m in msg_vnd:
                if len(m):
                    if 'sem_contrato' in m[0]:
                        msg += '<p>Linha sem Contrato - %s </p>' %(m[0]['sem_contrato'])
                    if 'sem_linha' in m[0]:
                        msg += '<p>Linha nao Cadastrada - %s </p>' % (m[0]['sem_linha'])
                    if 'erro_add' in m[0]:
                        msg += '<p>Erro adicionar pedido - %s </p>' % (m[0]['erro_add'])
                    if 'erro_inc' in m[0]:
                        msg += '<p>Erro incluir pedido - %s </p>' % (m[0]['erro_inc'])

                print "teste"
            self.message_post(body=_(msg))

    # ja esta pegando tudo nao preciso disto
    def _parse_febraban_sms(self, data_file, raise_error=False):
        cnab240_file = tempfile.NamedTemporaryFile()
        cnab240_file.write(data_file)
        cnab240_file.flush()
        #arquivo = Arquivo(claro, arquivo=open(, 'r'))
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'servico.json')
        ff = Fixed_files(file_path, dic=False, checklength=False)
        records = open(cnab240_file.name).readlines()
        rec_in = []
        for record in records:
            # 10 RESUMO VALOR DAS LIGACOES E GASTOS SERVICOS
            # O QUE EU PRECISO PARA JOGAR NA FATURA
            if record[0] == '4':
                rec_in.append(ff.parse(record))

        msg_vnd = []
        for n, r in enumerate(rec_in):
            vlt = 0.00
            if r.valor_servico_cimp > 0:
                vlt = float(r.valor_total_geral)/100
            if vlt > 0.00:
                msg_vnd.append(self.cria_venda(r.data_emissao
                       ,r.numero_recurso.strip()
                       ,r.mes_referencia
                       ,0
                       ,0
                       ,vlt
                       ,0
                ))
        """
        if len(msg_vnd):
            msg = ''
            for m in msg_vnd:
                if len(m):
                    if 'sem_contrato' in m[0]:
                        msg += '<p>Linha sem Contrato - %s </p>' %(m[0]['sem_contrato'])
                    if 'sem_linha' in m[0]:
                        msg += '<p>Linha nao Cadastrada - %s </p>' % (m[0]['sem_linha'])
                    if 'erro_add' in m[0]:
                        msg += '<p>Erro adicionar pedido - %s </p>' % (m[0]['erro_add'])
                    if 'erro_inc' in m[0]:
                        msg += '<p>Erro incluir pedido - %s </p>' % (m[0]['erro_inc'])

                print "teste"
            self.message_post(body=_(msg))
        """


    def import_to_db(self):
        self._parse_febraban(base64.b64decode(self.input_file))
        self.confirma_vendas(self.vendas_ids)
        del self.vendas_ids[:]
        return True