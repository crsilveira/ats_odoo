# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):

    _inherit = "sale.order"

    os_descr = fields.Text(string=u"Mensagem O.S.")
    os_descr_int = fields.Text(string=u"Mensagem Interna O.S.")

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        contract = self.env['account.analytic.account']
        task = self.env['project.task.install']
        vals = {}
        order_line=[]
        if self.order_line_serv:
            crt = self.env['account.analytic.account'].search([('partner_id','=',self.partner_id.id)],limit=1)
            if crt:
                order_line = []
                for line in self.order_line_serv:
                    order_line.append((0,0,{
                        'product_id': line.product_id.id,
                        'price_unit': line.price_unit,
                        'quantity': line.product_uom_qty,
                        'name': line.product_id.name + ' (ADITIVO)',
                        'uom_id': line.product_id.uom_id.id
                    }))
                    vals = {}
                vals['recurring_invoice_line_ids'] = order_line
                crt.sudo().write(vals)
                self.create_task(task, crt)
                return True
            vals['manager_id'] = self.user_id.id
            vals['partner_id'] = self.partner_id.id
            vals['code'] = self.env['ir.sequence'].next_by_code('contract.sequence.code')
            vals['name'] = vals['code']
            vals['use_tasks'] = True
            vals['recurring_invoices'] = True
            vals['payment_mode_id'] = self.ctr_payment_mode_id.id
            vals['payment_term_id'] = self.ctr_payment_term_id.id
            vals['recurring_next_date'] = self.recurring_next_date
            for line in self.order_line_serv:
                order_line.append((0,0,{
                    'product_id' : line.product_id.id,
                    'price_unit' : line.price_unit,
                    'quantity' : line.product_uom_qty,
                    'name' : line.product_id.name,
                    'uom_id' : 1
                }))
            vals['recurring_invoice_line_ids'] = order_line
        if len(vals):
            id_contract = contract.sudo().create(vals)
            msg_crt = u'Criado contrato número: %s' %(id_contract.code)
            self.message_post(body=_(msg_crt))
            if id_contract:
                self.create_task(task, id_contract)
        return True

    def create_task(self, task, id_ctr):
        vals = {}
        linha = []
        project = self.env['project.project'].sudo().search([('analytic_account_id','=',id_ctr.id)])
        if self.order_line:
            vals['partner_id'] = self.partner_id.id
            vals['project_id'] = project.id
            #vals['stage_id'] = 1
            vals['company_id'] = self.company_id.id
            vals['name'] = self.partner_id.name
            vals['vendor_id'] = self.user_id.id
            vals['ref'] = id_ctr.code
            vals['status_bar'] = 'waiting'
            vals['int_msg'] = self.os_descr_int
            if self.os_descr:
                vals['description'] = u'Descrição da venda: ' + self.os_descr + u'<br/>Serviços contratados:'
            else:
                vals['description'] = u'<br/>Serviços contratados:'
            for line in id_ctr.recurring_invoice_line_ids:
                vals['description'] += ' ' + line.name + '\n'
            os = task.sudo().create(vals)
            os._onchange_project();
        for line in self.order_line:
            linha.append(
                (0, 0, {
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
            })
            )
            task_sale = {'material_ids':linha, 'user_id':False}
            os.sudo().write(task_sale)
            linha = []

        msg_task = u'Criado OS de instalação número: %s' % (os.code)
        self.message_post(body=_(msg_task))
        return vals






