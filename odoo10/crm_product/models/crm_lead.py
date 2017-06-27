#  -*- encoding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError, AccessError


class CrmLead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    sent = fields.Boolean(string="Proposta enviada")

    productsite_id = fields.Many2one('crm.productsite', 'Produto', required=True)
    is_company = fields.Boolean('P. Juridica')
    mobile= fields.Char('Mobile')
    origem_lead= fields.Selection([
        ('C','Chat'), 
        ('E','Email'),
        ('F','Fone'), 
        ('S','Site'), 
        ('W','Whatsapp'),
        ('I', 'Indicacao'),
        ('O','Outros')],
        'Origem Lead', index=True, required=True)
    pref_contato= fields.Selection([
        ('C','Chat'), 
        ('E','Email'),
        ('F','Telefone'), 
        ('W','Whatsapp'),
        ('O','Outros')],
        'Preferência Contato', index=True, required=True)

    _defaults = {
        'country_id': 32,
        'state_id': 71
    }

    _order = 'create_date desc, priority desc'

    @api.model
    def create(self, vals):
        # verificar se quem esta inserindo e um vendedor
        user_id = self._uid
        if 'origem_lead' in vals:
            if not 'pref_contato' in vals:
                vals['pref_contato'] = vals.get('origem_lead') 
            #if vals.get('origem_lead') in ['E','F','W']:
            #    vals['origem_lead'] = 'S'
        #vals['origem_lead'] = 'Fone/Outros'
        if 'user_id' in vals:
            vend_obj = self.env['hr.employee']
            user_id = vend_obj.search([
                ('job_id', '=', 'Vendedor'),
                ('user_id','=', vals.get('user_id'))
            ]).user_id.id

            if not user_id:
               user_id = self._uid
               vals['user_id'] = self._uid
        # pegando as unidades, q nao distribui leads para SP
        un_obj = self.env['res.company']
        un_ids = un_obj.search([('partner_id.suframa', '!=', False)])
        lista_un = []
        for x in un_ids:
            if x.suframa:
                lista_un.append(x.id)


        ####  USUARIO TRAVADO MESMO DO SCRIPT SITE
        if user_id == 19 and 'company_id' in vals:
            vals['origem_lead'] = 'S'
            cp_id = vals.get('company_id')
            if int(cp_id) not in lista_un:
                hr_obj = self.env['hr.employee']
                hr_ids = hr_obj.search([('job_id', '=', 'Vendedor')])
                crm_ids = self.env["crm.lead"]
                search_ids = crm_ids.search([
                    ('company_id','not in',lista_un)
                    , ('origem_lead','=', ['S'])])
                last_id = search_ids and max(search_ids)
                #crm_id = crm_ids.browse([last_id])
                feito = 0
                vend = 0
                ultimo = 0
                for vendedor in hr_ids:
                    vend += 1
                    if last_id.user_id.id == vendedor.user_id.id:
                        ultimo = vend
                        continue

                if ultimo == len(hr_ids):
                    ultimo -= len(hr_ids)
                    vals['user_id'] = hr_ids[ultimo].user_id.id
                    feito = 1
                else:
                    vals['user_id'] = hr_ids[ultimo].user_id.id
                    feito = 1

                if feito == 0:
                    vals['user_id'] = hr_ids[0].user_id.id

                vals['type'] = 'opportunity'

        if 'email_from' in vals:
            crm_obj = self.env['crm.lead']
            email_from = vals.get('email_from')
            if email_from:
                email_from = email_from.strip()
            crm_ids = crm_obj.search([
                ('email_from', 'ilike', email_from),
                ('type', '=', 'opportunity')
            ])
            for lead in crm_ids:
                stage_id_lost = lead._stage_find(domain=[('probability', '=', 0.0), ('on_change', '=', True), ('sequence', '>', 1)])
                stage_id_won = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
                if not lead.stage_id.id in (stage_id_lost.id, stage_id_won.id):
                    raise UserError(_(u'Oportunidade duplicada\nJá existe uma oportunidade com este email!'))
        if 'name' in vals:
            if not 'productsite_id' in vals:
                prod = self.env['crm.productsite']
                prod_id = prod.search([('name','ilike', vals.get('name'))])
                if prod_id:
                    vals['productsite_id'] = prod_id.id
                else:
                    vals['productsite_id'] = 1

        if not 'name' in vals:
            prod = self.env['crm.productsite']
            prod_id = prod.browse([vals.get('productsite_id')])
            if prod_id:
                vals['name'] = prod_id.name

        # context: no_log, because subtype already handle this
        return super(CrmLead, self).create(vals)

    @api.multi
    def write(self,vals):
        if 'email_from' in vals:
            crm_obj = self.env['crm.lead']
            email_from = vals.get('email_from')
            if email_from:
                email_from = email_from.strip()
            crm_ids = crm_obj.search([
                ('email_from', 'ilike', email_from),
                ('type', '=', 'opportunity')
            ])
            for lead in crm_ids:
                stage_id_lost = lead._stage_find(domain=[('probability', '=', 0.0), ('on_change', '=', True), ('sequence', '>', 1)])
                stage_id_won = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
                if not lead.stage_id.id in (stage_id_lost.id, stage_id_won.id):
                    raise UserError(_(u'Oportunidade duplicada\nJá existe uma oportunidade com este email!'))
        # stage change: update date_last_stage_update
        partner_obj = self.env['res.partner']
        for lead in self.browse(self.id):
            if lead.stage_id.id == 6:
                if not lead.partner_id:
                    erro = ''
                    #if not lead.legal_name:
                    #    erro = u'Razão Social(Nome que saira no Contrato.)\n'
                    #if erro != '':
                    #    raise UserError(    
                    #        _(u'Dados incompletos!\n%s')) %(erro)

                    partner_id = 0
                    if lead.email_from:
                        partner_ids = partner_obj.search([('email', '=', lead.email_from)])
                        if partner_ids:
                            partner_id = partner_ids[0]
                    elif lead.cnpj:
                        partner_ids = partner_obj.search([('cnpj_cpf', '=', lead.cnpj)])
                        if partner_ids:
                            partner_id = partner_ids[0]
                    elif lead.cpf:
                        partner_ids = partner_obj.search([('cnpj_cpf', '=', lead.cpf)])
                        if partner_ids:
                            partner_id = partner_ids[0]
                    # Search through the existing partners based on the lead's partner or contact name
                    elif lead.partner_name:
                        partner_ids = partner_obj.search([('name', 'ilike', '%'+lead.partner_name+'%')])
                        if partner_ids:
                            partner_id = partner_ids[0]
                    elif lead.contact_name:
                        partner_ids = partner_obj.search([
                            ('name', 'ilike', '%'+lead.contact_name+'%')])
                        if partner_ids:
                            partner_id = partner_ids[0]
                    #if partner_id == 0:
                    #    partner_id = self._create_lead_partner(lead)
        if 'productsite_id' in vals:
            prod = self.env['crm.productsite'].browse(vals.get('productsite_id'))
            vals['name'] = prod.name

        return super(CrmLead, self).write(vals)

    @api.onchange('productsite_id')
    def _onchange_productsite_id(self):
        if self.productsite_id:
            self.name = self.productsite_id.name

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.is_company = self.partner_id.is_company
            self.phone = self.partner_id.phone
            self.mobile = self.partner_id.mobile
            self.email_from = self.partner_id.email
            self.street = self.partner_id.street
            self.street2 = self.partner_id.street2
            self.state_id = self.partner_id.state_id
            self.country_id = self.partner_id.country_id
            self.zip = self.partner_id.zip
        return super(CrmLead, self)._onchange_partner_id()


    """


    """


    @api.model
    def gerar_tarefas(self, partner_id, company_id):
        project_id = self.env['project.project'].search([('name','=','Cadastro'),('partner_id.company_id','=',company_id)])
        if project_id:
            task = 'Cadastrar - %s' % (partner_id.name)
            self.env['project.task'].sudo().create({
                'name': task,
                'user_id': False,
                'project_id': project_id.id,
                'description': 'Verificar todas as informações, e criar o contrato',
                'partner_id' : partner_id.id
            })
        else:
            project_id = self.env['project.project'].search([('name', '=', 'Cadastro'),('partner_id','=',False)])
            #for seguidor in project.message_follower_ids:
            if project_id:
                task = 'Cadastrar - %s' %(partner_id.name)
                self.env['project.task'].sudo().create({
                    'name': task,
                    'user_id': False,
                    'project_id': project_id.id,
                    'description': 'Verificar todas as informações, e criar o contrato',
                    'partner_id' : partner_id.id,
                    'company_id' : False
                })
        project_id = self.env['project.project'].search([('name', '=', 'Atendimento'),('partner_id.company_id','=',company_id)])
        if project_id:
            task = 'Atendimento - %s' % (partner_id.name)
            self.env['project.task'].sudo().create({
                'name': task,
                'user_id': False,
                'project_id': project_id.id,
                'description': 'Cadastrar dados necessários para o Atendimento.',
                'partner_id' : partner_id.id
            })
        else:
            project_id = self.env['project.project'].search([('name', '=', 'Atendimento'),('partner_id','=',False)])
            if project_id:
               task = 'Atendimento - %s' %(partner_id.name)
               self.env['project.task'].sudo().create({
                   'name': task,
                   'user_id': False,
                   'project_id': project_id.id,
                   'description': 'Cadastrar dados necessários para o Atendimento.',
                   'partner_id' : partner_id.id,
                   'company_id' : False
               })

        project_id = self.env['project.project'].search([('name', '=', 'Financeiro'),('partner_id.company_id','=',company_id)])
        if project_id:
            task = 'Conferir Cadastro - %s' % (partner_id.name)
            self.env['project.task'].sudo().create({
                'name': task,
                'user_id': False,
                'project_id': project_id.id,
                'description': 'Conferir campos obrigatórios para gerar o faturamento',
                'partner_id' : partner_id.id
            })
        else:
            project_id = self.env['project.project'].search([('name', '=', 'Financeiro'),('partner_id','=',False)])
            if project_id:
               task = 'Conferir Cadastro - %s' %(partner_id.name)
               self.env['project.task'].sudo().create({
                  'name': task,
                  'user_id': False,
                  'project_id': project_id.id,
                  'description': 'Conferir campos obrigatórios para gerar o faturamento',
                  'partner_id' : partner_id.id,
                  'company_id' : False
               })

        project_id = self.env['project.project'].search([('name', '=', 'Telefonia'),('partner_id.company_id','=',company_id)])
        if project_id:
            task = 'Telefonia - %s' % (partner_id.name)
            self.env['project.task'].sudo().create({
                'name': task,
                'user_id': False,
                'project_id': project_id.id,
                'description': 'Ativar telefone e ramais para o cliente novo !',
                'partner_id' : partner_id.id
            })
        else:
            project_id = self.env['project.project'].search([('name', '=', 'Telefonia'),('partner_id','=',False)])
            if project_id:
               task = 'Telefonia - %s' %(partner_id.name)
               self.env['project.task'].sudo().create({
                   'name': task,
                   'user_id': False,
                   'project_id': project_id.id,
                   'description': 'Ativar telefone e ramais para o cliente novo !',
                   'partner_id' : partner_id.id,
                   'company_id' : False
               })


    def envia_boas_vindas_email(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('crm_product', 'boasvindas_email_template')[1]
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
        except ValueError:
            template_id = False

    @api.multi
    def _lead_create_contact(self, name, is_company, parent_id=False):
        email_split = tools.email_split(self.email_from)
        values = {
            'name': name,
            'user_id': self.user_id.id,
            'comment': self.description,
            'team_id': self.team_id.id,
            'parent_id': parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': email_split[0] if email_split else False,
            'fax': self.fax,
            'title': self.title.id,
            'function': self.function,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'is_company': is_company,
            'company_id': self.company_id.id,
            'legal_name': self.legal_name,
            'type': 'contact'
        }
        return self.env['res.partner'].create(values)

    @api.multi
    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            try:
                partner_id = self._lead_create_contact(lead.partner_name, lead.is_company, False)
                self.partner_id = partner_id
            except:
                pass
            stage_id = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 100})
            self.envia_boas_vindas_email()
            self.gerar_tarefas(lead.partner_id,lead.company_id.id)
        return True


