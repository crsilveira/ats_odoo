# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time


from odoo.addons.br_boleto.boleto.document import Boleto

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    email_fat = {}

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

        if not empresa.partner_id.legal_name:
            msg_erro += u'Empresa - Razão Social\n'
        if not empresa.cnpj_cpf:
            msg_erro += u'Empresa - CNPJ\n'
        if not empresa.district:
            msg_erro += u'Empresa - Bairro\n'
        if not empresa.zip:
            msg_erro += u'Empresa - CEP\n'
        if not empresa.city_id.name:
            msg_erro += u'Empresa - Cidade\n'
        if not empresa.street:
            msg_erro += u'Empresa - Logradouro\n'
        if not empresa.number:
            msg_erro += u'Empresa - Número\n'
        if not empresa.state_id.code:
            msg_erro += u'Empresa - Estado\n'

        # valida contrato (cliente, empresa, unidade, produto)
        if not contrato.partner_id:
            msg_inc.append({'cadastro': 'Contrato %s sem cliente definido.' % (contrato.name)})
            msg_erro = msg_erro + 'Contrato sem cliente definido; '
        else:
            cli = contrato.partner_id

            if not cli.name:
                msg_erro += u'Cliente - Nome\n'
            if cli.is_company and \
                    not cli.legal_name:
                msg_erro += u'Cliente - Razão Social\n'
            if not cli.cnpj_cpf:
                msg_erro += u'Cliente - CNPJ/CPF \n'
            if not cli.district:
                msg_erro += u'Cliente - Bairro\n'
            if not cli.zip:
                msg_erro += u'Cliente - CEP\n'
            if not cli.city_id.name:
                msg_erro += u'Cliente - Cidade\n'
            if not cli.street:
                msg_erro += u'Cliente - Logradouro\n'
            if not cli.number:
                msg_erro += u'Cliente - Número\n'
            if not cli.state_id.code:
                msg_erro += u'Cliente - Estado\n'

            if not contrato.payment_term_id and not cli.property_payment_term_id:
                msg_erro = msg_erro + u'Falta Condicoes de Pagamento do Cliente; '
            if not contrato.payment_mode_id and not cli.payment_mode_id:
                msg_erro = msg_erro + u'Falta Modo de Pagamento do Cliente; '
            if not contrato.fiscal_position_id and not cli.property_account_position_id:
                msg_erro = msg_erro + u'Falta Posicao Fiscal; '
            if not contrato.payment_mode_id.bank_account_id.codigo_convenio:
                msg_erro += u'Código de Convênio\n'

            #if empresa.id != cli.company_id.id:
            #    msg_erro = msg_erro + u'Empresa no contrato diferente do cadastro do cliente; '
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
        msg_erro = ''
        try:
            msg_erro = 'Erro para criar pedido de venda.'
            invoice_ids.append(self.env['sale.order'].create(invoice_vals))
            msg_erro = 'Erro para adicionar itens pedido de venda.'
            self._prepare_order_lines(self, invoice_ids[0])
            msg_erro = 'Erro pra confirmar pedido de venda.'
            invoice_ids[0].action_confirm()
            msg_erro = 'Erro para criar a Fatura.'
            inv_id = self.faturar_invoice()
            invoice = self.env['account.invoice'].browse(inv_id)
            if not invoice.payment_mode_id:
                pay = {}
                if self.payment_mode_id:
                    pay['payment_mode_id'] = self.payment_mode_id.id
                    invoice.write(pay)
            msg_erro = 'Erro para Confirmar a Fatura.'
            invoice.action_invoice_open()
            if invoice.payment_mode_id.boleto_type:
                msg_erro = 'Erro para Gerar o Boleto.'
                self.criar_boleto(invoice.id, invoice.receivable_move_line_ids[0])
            msg_erro = ''
            self.relatorio_faturamento('SIM', self.id, self.code, self.partner_id.name, '',
                'NAO', self.company_id.name)
            return invoice, msg_erro
        except Exception:
            self.env.cr.rollback()
            return False, msg_erro

    @api.multi
    def recurring_create_invoice(self):
        context = {}
        email_line = {}
        email_rel = {}
        for contract in self:
            if not contract.active:
                continue
            if not contract.partner_id.active:
                continue
            context['cliente'] = contract.partner_id
            context['contrato'] = contract
            context['empresa'] = contract.company_id
            context['id_contrato'] = contract.id
            valido = self.validando_info(context)
            if len(valido):
                #email_line = {'faturado':'NAO',
                #    'contrato': contract.code,
                #    'cliente': contract.partner_id.name,
                #    'ocorrencia': valido
                #}
                email_dados = email_rel.setdefault(id,email_line)
                email_dados.setdefault('NAO FATURADO', {})
                email_dados = 'Erro : %s' %(valido)
                contract.message_post(body=_())
                continue

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
            inv, msg = contract.with_context(ctx)._create_invoice()
            if inv:
                contract.write({
                    'recurring_next_date': new_date.strftime('%Y-%m-%d')
                })
                self.env.cr.commit()
            else:
                msg = 'Erro no faturamento,  ' + msg
                contract.message_post(body=_(msg))
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
    def cron_recurring_create_invoice(self, company):
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('recurring_invoices', '=', True),
             ('company_id','=',company),
             ('active','=',True)])
        return contracts.recurring_create_invoice()

    def _prepare_order_lines(self, contract, order_id):
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            invoice_lines = []
            if line.date_start and line.date_stop:
                if line.date_start <= self.recurring_next_date and line.date_stop > self.recurring_next_date:
                    invoice_lines = {
                        'order_id': order_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
                    }
            elif line.date_start and not line.date_stop:
                if line.date_start <= self.recurring_next_date:
                    invoice_lines = {
                        'order_id': order_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
                    }
            elif not line.date_start and line.date_stop:
                if line.date_stop > self.recurring_next_date:
                    invoice_lines = {
                        'order_id': order_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
                    }
            else:
                invoice_lines = {
                    'order_id': order_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit or 0.0,
                    'product_uom_qty': line.quantity,
                    'product_id': line.product_id.id or False,
                }

            if len(invoice_lines):
                self.env['sale.order.line'].create(invoice_lines)
        return invoice_lines
