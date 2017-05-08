# -*- coding: utf-8 -*-

import logging
import tempfile
import StringIO

from datetime import datetime
from odoo import fields, models
from odoo.exceptions import UserError

try:
    from cnab240.bancos import itau
    from cnab240.tipos import Arquivo
    from ofxparse import OfxParser
except ImportError:
    _logger.debug('Cannot import cnab240 or ofxparse dependencies.')

_logger = logging.getLogger(__name__)

class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _alterar_status_fatura(self, inv_id, arquivo):
        acc_ids = self.env['account.invoice'].browse(inv_id)
        if acc_ids:
            #vals =
            #vals['state'] = 'renegociado'
            acc_ids.write({'state':'renegociado', 'name': arquivo})



    def _parse_cnab(self, data_file, raise_error=False):

        """
        LEIO os dados aqui mas o tipo 9 nao vem
        res = super(AccountBankStatementImport, self)._parse_cnab(data_file, raise_error)
        x,y,z = res
        tr = z[0]['transactions']
        for ln in tr:
            print ln['name']
            print ln['partner_name']
            print ln['ref']
        """

        cnab240_file = tempfile.NamedTemporaryFile()
        cnab240_file.write(data_file)
        cnab240_file.flush()

        #arquivo = Arquivo(sicoob, arquivo=open(cnab240_file.name, 'r'))
        arquivo = Arquivo(itau, arquivo=open(cnab240_file.name, 'r'))
        transacoes = []

        inicio = datetime.strptime(str(arquivo.header.arquivo_data_de_geracao), '%d%m%Y')
        final = datetime.strptime(str(arquivo.header.arquivo_data_de_geracao), '%d%m%Y')
        #import pudb;pu.db
        cod_arquivo = str(arquivo.header.arquivo_sequencia+arquivo.header.cedente_conta)
        n_arq = '%s - %s - %s' % (
            arquivo.header.cedente_conta,
            inicio.strftime('%d/%m/%Y'),
            final.strftime('%d/%m/%Y'))

        company_id = 1
        if self.force_journal_account:
            if not self.journal_id.company_id:
                raise UserError(u"Informe a Empresa na Conta Selecionada")
            company_id = str(self.journal_id.company_id.id)
        else:
            raise UserError(u"Informe a Conta")
        len_company = len(company_id)
        for lote in arquivo.lotes:
            for evento in lote.eventos:
                if evento.servico_codigo_movimento not in (6,8, 9,10):
                    continue
                n_doc = '0'
                if evento.numero_documento:
                    c_doc = len(evento.numero_documento)
                    if c_doc > 7:
                        try:
                            pos_doc = evento.numero_documento.index('/')
                            n_doc = evento.numero_documento[:pos_doc]
                            # coloquei aqui pois os titulos velhos nao tem a empresa na frente
                            if company_id != n_doc[:len_company]:
                                continue
                        except:
                            n_doc = evento.numero_documento
                    else:
                        n_doc = evento.numero_documento


                    prt = self.env['account.invoice'].search([
                        ('number','ilike',evento.numero_documento)
                    ], limit=1)
                    prt_id = 0
                    if prt:
                        sacado = prt.partner_id.name
                        prt_id = prt.partner_id.id
                    else:
                        sacado = evento.sacado_nome

                    if evento.servico_codigo_movimento == 9:
                        self._alterar_status_fatura(prt.id, n_arq)
                        continue

                #valor = evento.valor_lancamento
                valor = evento.valor_titulo
                #if evento.tipo_lancamento == 'D':
                #    valor *= -1
                if evento.data_credito == 0:
                    dta_credito = evento.data_ocorrencia
                else:
                    dta_credito = evento.data_credito
                cod_arquivo += n_doc
                transacoes.append({
                    'name': n_doc,
                    'date': datetime.strptime(
                        str(dta_credito), '%d%m%Y'),
                    'amount': valor,
                    'partner_name': sacado,
                    'ref': n_doc,
                    'unique_import_id': str(cod_arquivo),
                })
        header = arquivo.lotes[0].header
        trailer = arquivo.lotes[0].trailer

        vals_bank_statement = {
            'name': u"%s - %s até %s" % (
                arquivo.header.nome_do_banco,
                inicio.strftime('%d/%m/%Y'),
                final.strftime('%d/%m/%Y')),
            'date': inicio,
            'balance_start': 0.0, # arquivo.lotes[0].header.valor_saldo_inicial,
            'balance_end_real': 0.0, #arquivo.lotes[0].trailer.valor_saldo_final,
            'transactions': transacoes
        }
        account_number = str(arquivo.header.cedente_conta)
        if self.force_journal_account:
            account_number = self.journal_id.bank_acc_number
        return (
            'BRL', #arquivo.lotes[0].header.moeda,
            account_number,
            [vals_bank_statement]
        )

        return res