# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time

from odoo.addons.br_boleto.boleto.document import Boleto

class ContractReajuste(models.Model):
    _name = "account.analytic.reajuste"

    reajuste_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    product_id = fields.Many2one('product.product','Produto')
    user_id = fields.Many2one('res.users','Usuário')
    name = fields.Date(u'Data Reajuste')
    valor_anterior = fields.Float(u'Valor Anterior')
    indice = fields.Float(u'Indice aplicado')


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    email_fat = {}
    """
    def _v_total(self):
        res = {}
        return res

    def _get_order(self):
        result = {}
        for line in self.env['account.analytic.invoice.line'].browse([self.id]):
            result[line.order_id.id] = True
        return result.keys()
    """

    def _total_contrato(self):
        val = 0.0
        res = dict([(i, {}) for i in ids])
        for account in self:
            val = account.recurring_invoice_line_ids.quantity * account.recurring_invoice_line_ids.price_unit
            res[account.id]['valor_total'] = val
        return res

    valor_total = fields.Float('Valor Total')
    reajuste_ids = fields.One2many('account.analytic.reajuste', 'reajuste_id', 'Historico reajuste', copy=False)
    motivo_encerramento = fields.Selection([
            ('1003', '1003-Problemas Financeiros'),
            ('1004', '1004-Encerramento Atividades'),
            ('1005', '1005-Mudou-se de endereço'),
            ('1006', '1006-Foi pra concorrência melhor preço'),
            ('1007', '1007-Foi pra concorrência descontentamento'),
            ('1544', '1544-Problemas no orçamento'),
            ('2009', '2009-Entrega do imovel'),
            ('2010', '2010-Optou por ficar com o atendimento de uma única empresa'),
            ('2012', '2012-Por não ter serviço específico'),
            ('2411', '2411-Cancelado por Inadimplência'),
            ('2641', '2641-Cadastro em duplicidade'),
            ('2642', '2642-Falecimento'),
            ], 'Motivo de Encerramento', help="Motivo pelo qual o contrato foi finalizado.")

    @api.model
    def create(self, vals):
        if 'recurring_invoice_line_ids' in vals:
            for x in vals.get('recurring_invoice_line_ids'):
                p = 0.0
                q = 0.0
                if 'price_unit' in x[2]:
                    p = x[2].get('price_unit')
                if 'quantity' in x[2]:
                    q = x[2].get('quantity')
                vt = p * q
                vals['valor_total'] = vt
        contract_id = super(AccountAnalyticAccount,self).create(vals)
        if 'recurring_invoice_line_ids' in vals:
            for x in vals.get('recurring_invoice_line_ids'):
                if 'product_id' in x[2]:
                    #prod_ids = prod_obj.search(cr, uid, [('id','=',x[2].get('product_id'))],context=context)
                    #for prod in prod_obj.browse(cr, uid, prod_ids, context=context):
                    #    prod_obj.write(cr, uid, [prod.id], {'contract_id': contract_id}, context=context)
                    prod = self.env['product.template'].browse([x[2].get('product_id').id])
                    prod.write({'contract_id': contract_id})
        return contract_id

    @api.multi
    def write(self, values):
        for account in self:
            if 'recurring_invoice_line_ids' in values:
                val = 0.0
                for x in vals.get('recurring_invoice_line_ids') :
                    p = 0.0
                    q = 0.0
                    vt = 0.0
                    if x[2] and 'price_unit' in x[2]:
                        p = x[2].get('price_unit')
                    if x[2] and 'quantity' in x[2]:
                        q = x[2].get('quantity')
                    if p > 0 and q > 0:
                        vt = p * q
                    elif p > 0:
                        vt = p * account.recurring_invoice_line_ids.quantity
                    elif q > 0:
                        vt = q * account.recurring_invoice_line_ids.price_unit
                    if vt > 0:
                        val = vt
                    if x[2] and 'product_id' in x[2]:
                        prod = self.env['product.template'].browse([x[2].get('product_id').id])
                        prod.write({'contract_id': account.id})
                        #prod_obj = self.pool.get('product.template')
                        #prod_ids = prod_obj.search(cr, uid, [('id','=',x[2].get('product_id'))],context=context)
                        #for prod in prod_obj.browse(cr, uid, prod_ids, context=context):
                        #    prod_obj.write(cr, uid, [prod.id], {'contract_id': account.id}, context=context)
                values['valor_total'] = val
        return super(AccountAnalyticAccount,self).write(values)

    def relatorio_contrato_erro(self):
        """
            -Vou buscar direto nos contratos os que foram faturados ou nao
            -pegar as faturas nao confirmadas
            -pegar faturas confirmadas sem boleto
            -pegar faturas confirmadas com boletos
            e exibir tudo em um email
        """
        email_line = {}
        email_rel = {}
        context = {}
        current_date =  time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search([
                ('recurring_next_date','<=', current_date),
                ('state','=', 'open'),
                ('recurring_invoices','=', True),
                ('type', '=', 'contract')])
        # CONTRATOS QUE NAO FORAM FATURADOS E PERMANECEM COM A MESMA DATA DE RECORRENCIA
        if contract_ids:
            #cr.execute('SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s\
            # GROUP BY company_id', (tuple(contract_ids),))
            #for company_id, ids in cr.fetchall():
            #for company_id, ids in contract_ids:
            #    d_val['empresa'] = company_id
            for contract in self.browse(contract_ids):
                #d_val['empresa'] = contract.company_id
                #d_val['contrato'] = contract
                #d_val['cliente'] = contract.partner_id
                context['empresa'] = contract.company_id
                context['cliente'] = contract.partner_id.id
                context['contrato'] = contract.code
                context['id_contrato'] = contract.id
                valido = self.validando_info(context)
                if len(valido):
                    email_line = {'faturado':'NAO',
                        'contrato': contract.code,
                        'cliente': contract.partner_id.name,
                        'ocorrencia': valido
                    }
                    email_dados = email_rel.setdefault(id,email_line)
                    email_retorno = email_dados.setdefault('NAO FATURADO', {})
                    continue
            if len(email_rel):
                #template_id =self.env['ir.model.data'].get_object_reference(cr,uid, 'seg_contract','email_erro_fatura')[1]
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
                except ValueError:
                    template_id = False
                context['data'] = email_rel
                #self.pool.get('email.template').send_mail(cr, uid,template_id, uid, force_send=True, context=context)
                #self.env['email.template'].send_mail(
                #    self.env.cr, self.env.uid, template.id, self.id, force_send=True,
                #    context=context)
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def relatorio_faturamento(self, faturado, id, contrato, cliente, ocorrencia, enviar, unidade):
        context = {}
        email_txt = {}
        if faturado == 'NAO':
            email_txt = {'faturado':'NAO',
                        'contrato': contrato,
                        'cliente': cliente,
                        'ocorrencia': ocorrencia,
                        'unidade': unidade
                    }
            email_data = self.email_fat.setdefault(id,email_txt)
            email_return = email_data.setdefault('NAO FATURADO', {})
        if faturado == 'SIM':
            email_txt = {'faturado':'SIM',
                        'contrato': contrato,
                        'cliente': cliente,
                        'ocorrencia': '',
                        'unidade': unidade
                    }
            email_data = self.email_fat.setdefault(id,email_txt)
            email_return = email_data.setdefault('FATURADO', {})
        if enviar == 'SIM':
            #template_id =self.pool.get('ir.model.data').get_object_reference(cr,uid, 'seg_contract','email_erro_fatura')[1]
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
            except ValueError:
                template_id = False
            context['data'] = self.email_fat.items()
            #self.pool.get('email.template').send_mail(cr, uid,template_id, uid, force_send=True, context=context)
            #self.env['email.template'].send_mail(
            #    self.env.cr, self.env.uid, template.id, self.id, force_send=True,
            #    context=context)
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def validando_info(self, context=None):
        msg_inc = []
        if context:
            empresa = context.get('empresa')
            #cliente = context.get('cliente')
            contrato = context.get('contrato')
        msg_erro = ''
        # validando diario da empresa
        journal_obj = self.env['account.journal']
        journal_ids = journal_obj.search([('type', '=','sale'),('company_id', '=', empresa.id or False)], limit=1)
        if not journal_ids:
            msg_inc.append({'cadastro': 'Sem Diário : %s' %(empresa.name)})
            msg_erro = 'Defina um diario para a empresa; %s.' %(empresa.name)
        # valida contrato (cliente, empresa, unidade, produto)
        if not contrato.partner_id:
            msg_inc.append({'cadastro': 'Contrato %s sem cliente definido.' % (contrato.name)})
            msg_erro = msg_erro + 'Contrato sem cliente definido; '
        else:
            cli = contrato.partner_id
            # dados necessario para gerar o boleto
            if not cli.cnpj_cpf \
                    or not cli.legal_name \
                    or not cli.zip \
                    or not cli.street \
                    or not cli.number \
                    or not cli.city_id \
                    or not cli.district \
                    or not cli.state_id \
                    or not cli.country_id:
                msg_erro = msg_erro + u'Falta CNPJ/CPF, Contratante, Endereco completo; '
            if not contrato.payment_term_id and not cli.property_payment_term_id:
                msg_erro = msg_erro + u'Falta Condicoes de Pagamento do Cliente; '
            if not contrato.payment_mode_id and not cli.payment_mode_id:
                msg_erro = msg_erro + u'Falta Modo de Pagamento do Cliente; '
            if not contrato.fiscal_position_id and not cli.property_account_position_id:
                msg_erro = msg_erro + u'Falta Posicao Fiscal; '

            if empresa.id != cli.company_id.id:
                msg_erro = msg_erro + u'Empresa no contrato diferente do cadastro do cliente; '
            if empresa.id != cli.property_account_receivable_id.company_id.id:
                msg_erro = msg_erro +  u'Conta de Recebimento nao pertence a empresa do contrato; '
            #if empresa.id != cli.property_account_position_id.company_id.id:
            #    msg_erro = msg_erro + u'Posicao Fiscal nao pertence a empresa do contrato; '
            if len(msg_erro):
                msg_inc.append({'cadastro': msg_erro}) # TODO estou repetindo as msg aqui tem q tirar
                if len(msg_inc):
                    contrato.message_post(body=_(msg_inc))
            # fatura invalida
            venda = self.env['sale.order']
            venda_cli = venda.search([('state', '=', 'sale'),('partner_id','=', cli.id)])
            for sale_order in venda_cli:
                if sale_order.state != 'sale':
                    msg_erro = msg_erro + 'Fatura com status diferente de Manual %s; ' %(sale_order.name)

        # validar informacoes no contrato
        if empresa.id != contrato.company_id.id:
            msg_erro = msg_erro + u'Empresa diferente da Unidade no contrato; '

        return msg_erro

    """ 5 - Gerando o boleto """
    def criar_boleto(self, invoice, move):
        boleto_list = move.action_register_boleto()
        boleto_nome = '%s%s%s-%s.pdf' %(
                    move.date[8:11],
                    move.date[5:7],
                    move.date[0:4],
                    move.move_id.name
                )
        if not boleto_list:
            _logger.exception('Boleto nao gerado, contrato %s', context.get('contrato'))
            self.relatorio_faturamento(
                'NAO',
                id_invoice,
                context.get('contrato'),
                account_invoice.partner_id.name,
                'Boleto nao gerado.' ,
                'NAO',
                account_invoice.company_id.name
            )
            return False
        else:
            pdf_string = Boleto.get_pdfs(boleto_list).encode("base64")
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.create(
                {
                'name': boleto_nome,
                'datas': pdf_string,
                'datas_fname': boleto_nome,
                'res_model': 'account.invoice',
                'res_id': invoice,
                'type': 'binary'
            })
            return attachment_id

    """ 3 - Executa o faturamento das vendas existentes """
    def faturar_invoice(self):
        venda = self.env['sale.order']
        venda_ids = venda.search([
            ('partner_id','=',self.partner_id.id),
            ('state', '=', 'sale'),
            ('invoice_status', '=', 'to invoice')
        ])
        id = venda_ids.action_invoice_create()
        return id

    @api.multi
    def _create_invoice(self):
        invoice_ids = []
        invoice_vals = self._prepare_invoice()
        try:
            invoice_ids.append(self.env['sale.order'].create(invoice_vals))
            self._prepare_order_lines(self, invoice_ids[0])
            invoice_ids[0].action_confirm()
            inv_id = self.faturar_invoice()
            invoice = self.env['account.invoice'].browse(inv_id)
            if not invoice.payment_mode_id:
                pay = {}
                if self.payment_mode_id:
                    pay['payment_mode_id'] = self.payment_mode_id.id
                    invoice.write(pay)
            invoice.action_invoice_open()
            self.criar_boleto(invoice.id, invoice.receivable_move_line_ids[0])
            self.relatorio_faturamento('SIM', self.id, self.code, self.partner_id.name, '',
                'NAO', self.company_id.name)
            return invoice
        except Exception:
            return False

    @api.multi
    def recurring_create_invoice(self):
        context = {}
        email_line = {}
        email_rel = {}
        for contract in self:
            context['cliente'] = contract.partner_id
            context['contrato'] = contract
            context['empresa'] = contract.company_id
            context['id_contrato'] = contract.id
            valido = self.validando_info(context)
            """
            if len(valido):
                email_line = {'faturado':'NAO',
                    'contrato': contract.code,
                    'cliente': contract.partner_id.name,
                    'ocorrencia': valido
                }
                email_dados = email_rel.setdefault(id,email_line)
                email_dados.setdefault('NAO FATURADO', {})
                continue
            """
            old_date = fields.Date.from_string(
                contract.recurring_next_date or fields.Date.today())
            new_date = old_date + self.get_relative_delta(
                contract.recurring_rule_type, contract.recurring_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                # Force company for correct evaluate domain access rules
                'force_company': contract.company_id.id,
            })
            # Re-read contract with correct company
            if contract.with_context(ctx)._create_invoice():
                contract.write({
                    'recurring_next_date': new_date.strftime('%Y-%m-%d')
                })
            else:
                self.relatorio_faturamento('NAO', contract.id, contract.code, contract.partner_id.name,
                   'Erro ao executar o faturamento.', 'NAO', contract.company_id.name)
        if len(email_rel):
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
            except ValueError:
                template_id = False
            context['data'] = email_rel
            #self.env['mail.template'].browse(template_id).send_mail(contract.id, force_send=True)
        return True

    @api.model
    def cron_recurring_create_invoice(self):
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('recurring_invoices', '=', True)])
        return contracts.recurring_create_invoice()

    def _prepare_order_lines(self, contract, order_id):
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            invoice_lines = {
                'order_id': order_id.id,
                'name': line.name,
                'price_unit': line.price_unit or 0.0,
                'product_uom_qty': line.quantity,
                'product_id': line.product_id.id or False,
            }
            self.env['sale.order.line'].create(invoice_lines)
        return invoice_lines