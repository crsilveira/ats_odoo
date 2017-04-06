# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectIssue(models.Model):
    _inherit = "project.issue"

    legal_name = fields.Char(string='Razao Social',
                             related='partner_id.legal_name')
    fornece_fone = fields.Boolean(string='Fornec. Telefone ?',
                             related='partner_id.fornece_fone')
    fornece_email = fields.Boolean(string='Fornec. Email ?',
                                  related='partner_id.fornece_email')
    fornece_endereco = fields.Boolean(string='Fornec. Ender ?',
                                      related='partner_id.fornece_endereco')
    birthdate_n = fields.Date(string='Date de nascimento',
                              related='partner_id.birthdate_n')
    motivo_ausencia = fields.Char(string='Justificativa',
                                  related='partner_id.motivo_ausencia')
    transfer_recado = fields.Char(string='Tranferencia/Recado',
                                  related='partner_id.transfer_recado')
    razao_empresa = fields.Char(string='Razao-Empresa',
                                related='partner_id.razao_empresa')
    ramal_softphone1 = fields.Char(string='Fone Redirec.',
                                   related='partner_id.ramal_softphone1')
    ramal_softphone2 = fields.Char(string='Email Redirec.',
                                   related='partner_id.ramal_softphone2')
    email_financeiro = fields.Text(string='Email Financeiro',
                                   related='partner_id.email_financeiro')
    aviso_atendimento = fields.Char(string='Aviso Atendimento',
                                    related='partner_id.aviso_atendimento')
    pronuncia = fields.Char(string='Pronuncia',
                            related='partner_id.pronuncia')
    transferencia = fields.Boolean(string='Transferência',
                                  related='partner_id.transferencia')
    recado = fields.Boolean(string='Recado',
                            related='partner_id.recado')
    title = fields.Char(string='Ramo de Atividade',
                            relatec='partner_id.title')
    contato1 = fields.Html('Contato', store=False)
    contato2 = fields.Html('Contato', store=False)
    contato3 = fields.Html('Contato', store=False)
    endereco = fields.Char(string='Endereco', store=False)
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
    #partner_busca = fields.Many2one(
    #     string='Cliente', 'res.partner', search='_search_partner',
    #)

    """
    @api.one
    def _search_partner(self):
        # FAZER UM FOR POR CLIENTES E EXIBIR AQUI , JUNTNADO NOME, RAZAO EMAIL E PRONUNCIA
        import pudb;pu.db
        partner = self.env['res.partner'].search([('customer','=',True)])
        for prt in partner:
            names = [prt.name, prt.legal_name, prt.email, prt.pronuncia, prt.parent_id.name]
        self.partner_busca = ' / '.join(filter(None, names))
    """

    def action_atendimento_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        # cliente = self.pool.get('crm.claim').browse(cr, uid, ids, context=context)
        # if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", cliente.partner_id.email) != None:
        #    return True
        # else:
        #    raise osv.except_osv('Email inválido', 'Corrija o email no cadastro do Cliente.')
        #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            if self.partner_id.company_id.partner_id.aviso_atendimento:
                tmpl = str(self.partner_id.company_id.partner_id.aviso_atendimento)
                templ_id = self.env['mail.template'].search([("name", "=", tmpl)])
                template_id = templ_id[0].id
            else:
                template_id = ir_model_data.get_object_reference('project_issue_myplace', 'email_template_crm_claim')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'project.issue',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        vals['user_id'] = self._uid
        vals['date'] = fields.Datetime.now()
        return super(ProjectIssue, self).create(vals)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """This function returns value of partner address based on partner
           :param email: ignored
        """
        #import pudb;pudb.set_trace()
        if not self.partner_id:
            return {'value': {'email_from': False, 'partner_phone': False, 'legal_name': False, 'fornece_fone': False, 'title': False, 'fornece_email': False, 'motivo_ausencia': False, 'razao_empresa':False, 'transfer_recado': False, 'ramal_softphone1': False, 'ramal_softphone2': False, 'pronuncia': False, 'tem_contato': False}}
        address = self.env['res.partner'].browse(self.partner_id.id)
        contato1 = ''
        contato2 = ''
        contato3 = ''
        funcao = ''
        email = ''
        comment = ''
        coluna = 1
        linha = 1
        contato_html = '<address>'
        contato2_html = '<address>'
        contato3_html = '<address>'
        for contact in address.child_ids: 
            if contact.function:
                funcao = contact.function + '<br>'
            if contact.email:
                email = contact.email + '<br>'
            
            if linha == 1 and coluna == 1:
                contato1 = contato1 + '<strong>%s</strong><br> %s %s %s %s' %(contact.name, funcao, email, contact.phone or '', contact.mobile or '')
            if linha > 1 and coluna == 1:
                contato1 = contato1 + '<br><br><strong>%s</strong><br> %s %s %s %s' %(contact.name, funcao, email, contact.phone or '', contact.mobile or '')

            if linha == 1 and coluna == 2:
                contato2 = contato2 + '<strong>%s</strong><br> %s %s %s %s' %(contact.name, funcao, email, contact.phone or '', contact.mobile or '')
            if linha > 1 and coluna == 2:
                contato2 = contato2 + '<br><br><strong>%s</strong><br>%s %s %s %s' %(contact.name, funcao, email, contact.phone or '', contact.mobile or '')
            if linha == 1 and coluna == 3:
                contato3 = contato3 + '<strong>%s</strong><br> %s %s %s %s' %(contact.name, funcao, email, contact.phone or '', contact.mobile or '')
            if linha > 1 and coluna == 3:
                contato3 = contato3 + '<br><br><strong>%s</strong><br>%s %s %s %s' %(contact.name, funcao, email, contact.phone or '', contact.mobile or '')
            if coluna == 3:
                linha = linha + 1
            if coluna == 1:
                coluna = 2
            elif coluna == 2:
                coluna = 3
            else: 
                coluna = 1

        if contato1 != '':
            contato_html = contato_html + contato1 + '</address>'
        else:
            contato_html = ''
        if address.comment:
            comment = address.comment
        if contato2 != '':
            contato2_html = contato2_html + contato2 + '</address>'
        else:
            contato2_html = ''
        if contato3 != '':
            contato3_html = contato3_html + contato3 + '</address>'
        else:
            contato3_html = ''
        #pdb.set_trace()
        #if address.fornece_endereco:
        endereco_cliente = ''
        if address.company_id.street:
            endereco_cliente = address.company_id.street
        if address.company_id.number:
            endereco_cliente = endereco_cliente + ', ' +  address.company_id.number
        if address.company_id.street2:
            endereco_cliente = endereco_cliente + ' - ' +  address.company_id.street2
        if address.company_id.district:
            endereco_cliente = endereco_cliente + ' - ' +  address.company_id.district
        if address.company_id.city_id.name:
            endereco_cliente = endereco_cliente + ' - ' +  address.company_id.city_id.name
        #endereco_cliente = address.company_id.street + ', ' + address.company_id.number + ' - ' + address.company_id.district
        return {'value': {'email_from': address.email, 'partner_phone': address.fax, 'legal_name': address.legal_name, 'fornece_fone':address.fornece_fone, 'title': address.title.name, 'fornece_email':address.fornece_email, 'motivo_ausencia':address.motivo_ausencia, 'razao_empresa':address.razao_empresa, 'transfer_recado': address.transfer_recado, 'ramal_softphone1': address.ramal_softphone1, 'ramal_softphone2': address.ramal_softphone2, 'contato1': contato_html, 'contato2': contato2_html, 'fornece_endereco': address.fornece_endereco, 'endereco': endereco_cliente, 'aviso_atendimento': address.aviso_atendimento, 'pronuncia':address.pronuncia, 'contato3': contato3_html, 'comment': comment}}