# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class SaleReport(models.Model):
    """ CRM Opportunity Analysis """

    _name = "crm.product.sale.report"
    _auto = False
    _description = "Analise Vendas Crm"
    _rec_name = 'date_deadline'

    date_deadline = fields.Date('Fechamento Experado', readonly=True)
    create_date = fields.Datetime('Data Criada', readonly=True)
    opening_date = fields.Datetime('Data Iniciado', readonly=True)
    date_closed = fields.Datetime('Data Fechamento', readonly=True)
    date_last_stage_update = fields.Datetime('Ultima Atualizacao', readonly=True)
    active = fields.Boolean('Ativo', readonly=True)

    # durations
    delay_open = fields.Float('Prazo Abertura', digits=(16, 2), readonly=True, group_operator="avg", help="Number of Days to open the case")
    delay_close = fields.Float('Prazo Fechamento', digits=(16, 2), readonly=True, group_operator="avg", help="Number of Days to close the case")
    delay_expected = fields.Float('Prazo', digits=(16, 2), readonly=True, group_operator="avg")

    user_id = fields.Many2one('res.users', string='Vendedor', readonly=True)
    team_id = fields.Many2one('crm.team', 'Equipe Vendas', oldname='section_id', readonly=True)
    nbr_activities = fields.Integer('# Atividades', readonly=True)
    city = fields.Char('City')
    country_id = fields.Many2one('res.country', string='Pais', readonly=True)
    probability = fields.Float(string='Probabilidade', digits=(16, 2), readonly=True, group_operator="avg")
    total_revenue = fields.Float(string='Total', digits=(16, 2), readonly=True)
    expected_revenue = fields.Float(string='Turnover', digits=(16, 2), readonly=True)
    stage_id = fields.Many2one('crm.stage', string='Stagio', readonly=True, domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
    partner_id = fields.Many2one('res.partner', string='Cliente', readonly=True)
    company_id = fields.Many2one('res.company', string='Unidade', readonly=True)
    type = fields.Selection([
        ('lead', 'Lead'),
        ('opportunity', 'Oportunidade'),
    ], help="Type is used to separate Leads and Opportunities")
    lost_reason = fields.Many2one('crm.lost.reason', string='Razao perda', readonly=True)
    date_conversion = fields.Datetime(string='Data Conversão', readonly=True)
    campaign_id = fields.Many2one('utm.campaign', string='Campanha', readonly=True)
    source_id = fields.Many2one('utm.source', string='Origem', readonly=True)
    medium_id = fields.Many2one('utm.medium', string='Medium', readonly=True)

    numero_leads = fields.Integer(string='Numero Leads')
    productsite_id = fields.Many2one('crm.productsite', string='Produto', readonly=True)
    origem_lead = fields.Char(string='Origem Lead')
    pref_contato = fields.Char(string='Pref. Contato')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_product_sale_report')
        self._cr.execute("""
            CREATE VIEW crm_product_sale_report AS (
                SELECT
                    c.id,
                    c.date_deadline,

                    c.date_open as opening_date,
                    c.date_closed as date_closed,
                    c.date_last_stage_update as date_last_stage_update,
                    c.user_id,
                    c.probability,
                    c.stage_id,
                    c.type,
                    c.company_id,
                    c.team_id,
                    (SELECT COUNT(*)
                     FROM mail_message m
                     WHERE m.model = 'crm.lead' and m.res_id = c.id) as nbr_activities,
                    c.active,
                    c.campaign_id,
                    c.source_id,
                    c.medium_id,
                    c.partner_id,
                    c.city,
                    c.country_id,
                    c.planned_revenue as total_revenue,
                    c.planned_revenue*(c.probability/100) as expected_revenue,
                    c.create_date as create_date,
                    extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
                    abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
                    extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open,
                    c.lost_reason,
                    c.date_conversion as date_conversion,
                    COUNT(c.id) as numero_leads,
                    c.productsite_id,
                    CASE c.origem_lead WHEN 'C' THEN 'Chat'
                       WHEN 'E' THEN 'Email'
                       WHEN 'F' THEN 'Fone'
                       WHEN 'S' THEN 'Site'
                       WHEN 'W' THEN 'Whatsapp'
                       ELSE 'Outros' END as origem_lead,
                    CASE c.pref_contato WHEN 'C' THEN 'Chat'
                       WHEN 'E' THEN 'Email'
                       WHEN 'F' THEN 'Fone'
                       WHEN 'W' THEN 'Whatsapp'
                       ELSE 'Outros' END as pref_contato
                FROM
                    "crm_lead" c
                GROUP BY c.id, c.productsite_id
            )""")
