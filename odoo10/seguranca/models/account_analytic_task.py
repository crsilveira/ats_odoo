# -*- coding: utf-8 -*-
# © 2016 Carlos Silveira <crsilveira@gmail.com>, ATS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

class AccountAnalyticTaskLine(models.Model):
    _name = 'account.analytic.task.line'

    analytic_task_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    name = fields.Char(u'Descrição da Tarefa', size=128, required=True, index=True)
    project_id = fields.Many2one('project.project', 'Projeto', ondelete='set null', index=True)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    divisao = fields.Many2one(
        'company.type', 
        string="Divisão", 
        index=True,
        domain="[('company_id','=',company_id)]"
    )
    recurring_task_line_ids = fields.One2many('account.analytic.task.line', 'analytic_task_id', 'Linha de Tarefas', copy=True)
    recurring_task = fields.Boolean('Gerar tarefas recorrentes automaticamente')
    recurring_task_rule_type = fields.Selection([
            ('daily', 'Dia(s)'),
            ('weekly', 'Semana(s)'),
            ('monthly', 'Mes(es)'),
            ('yearly', 'Ano(s)'),
            ], 'Recorrencia', help='Cria tarefas automaticamente, em intervalos programados')
    recurring_task_interval = fields.Integer('Repetir cada', help="Repetir cada (Dia/Semana/Mes/Ano)")
    recurring_task_next_date = fields.Date('Data da proxima Tarefa')

    invoice_type = fields.Many2one('account.invoice.type', string='Tipo do faturamento', index=True)



    # Parei aqui a mudança para o odoo 10 25/11/16
    def onchange_recurring_tasks(self, cr, uid, ids, recurring_task, date_start=False, context=None):
        value = {}
        if date_start and recurring_task:
            value = {'value': {'recurring_task_next_date': date_start}}
        return value

    def recurring_create_task(self, cr, uid, ids, context=None):
        return self._recurring_create_task(cr, uid, ids, context=context)

    def _cron_recurring_create_task(self, cr, uid, context=None):
        return self._recurring_create_task(cr, uid, [], automatic=True, context=context)

    def _recurring_create_task(self, cr, uid, ids, automatic=False, context=None):
        context = context or {}
        # @@@@@@@@@@  CRIAR AQUI A ROTINA QUE CRIARA A TAREFA AGENDADA
        task_ids = []
        current_date =  time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search(cr, uid, [('recurring_task_next_date','<=', current_date), ('state','=', 'open'), ('recurring_task','=', True), ('type', '=', 'contract')])
        if contract_ids:
            cr.execute('SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s GROUP BY company_id', (tuple(contract_ids),))
            for company_id, ids in cr.fetchall():
                values = {}
                for contract in self.browse(cr, uid, ids, context=dict(context, company_id=company_id, force_company=company_id)):
                    try:
                        values['partner_id'] = contract.partner_id.id
                        task_name = ''
                        for task in contract.recurring_task_line_ids:
                            values['color'] = task.project_id.color
                            values['name'] = task.name + ' - ' + contract.code
                            values['project_id'] = task.project_id.id
                            values['user_id'] = None
                            values['code'] = self.pool.get('ir.sequence').get(cr, uid, 'project.task.tecnica')
                            task_ids.append(self.pool['project.task.tecnica'].create(cr, uid, values, context=context))
                        next_date = datetime.datetime.strptime(contract.recurring_task_next_date or current_date, "%Y-%m-%d")
                        interval = contract.recurring_task_interval
                        if contract.recurring_task_rule_type == 'daily':
                            new_date = next_date+relativedelta(days=+interval)
                        elif contract.recurring_task_rule_type == 'weekly':
                            new_date = next_date+relativedelta(weeks=+interval)
                        elif contract.recurring_task_rule_type == 'monthly':
                            new_date = next_date+relativedelta(months=+interval)
                        else:
                            new_date = next_date+relativedelta(years=+interval)
                        self.write(cr, uid, [contract.id], {'recurring_task_next_date': new_date.strftime('%Y-%m-%d')}, context=context)
                        if automatic:
                            cr.commit()
                    except Exception:
                        if automatic:
                            cr.rollback()
                            _logger.exception('Falha para criar tarefa no contrato %s', contract.code)
                        else:
                            raise
        return task_ids


class AccountInvoiceType(models.Model):
    _name = 'account.invoice.type'
    _description = "Invoice type"

    name = fields.Char('Nome')
    code = fields.Integer(string='Código')


