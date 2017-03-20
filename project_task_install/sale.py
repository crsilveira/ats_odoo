# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):

    _inherit = "sale.order"



    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        #super.action_confirm()
        contract = self.env['account.analytic.account']
        task = self.env['project.task.install']
        vals = {}
        linha = {}
        order_line=[]
        msg_task = ''
        msg_crt = ''
        if self.order_line_serv:
            vals['manager_id'] = self.user_id.id
            vals['partner_id'] = self.partner_id.id
            vals['name'] = self.partner_id.name
            vals['use_tasks'] = True
        for line in self.order_line_serv:
            #linha['product_id'] = line.product_id.id
            #linha['price_unit'] = line.price_unit
            #linha['quantity'] = line.product_uom_qty
            #linha['name'] = line.product_id.name
            #linha['uom_id'] = 1
            order_line.append((0,0,{
                'product_id' : line.product_id.id,
                'price_unit' : line.price_unit,
                'quantity' : line.product_uom_qty,
                'name' : line.product_id.name,
                'uom_id' : 1
            }))
        vals['recurring_invoice_line_ids'] = order_line
        if len(vals):
            id_contract = contract.create(vals)
            msg_crt = u'Criado contrato número: %s' %(id_contract.code)
            self.message_post(body=_(msg_crt))
            if id_contract:
                self.create_task(task, id_contract)
        return True



    def create_task(self, task, id_ctr):
        vals = {}
        linha = []
        project = self.env['project.project'].search([('analytic_account_id','=',id_ctr.id)])
        if self.order_line:
            vals['partner_id'] = self.partner_id.id
            vals['project_id'] = project.id
            vals['company_id'] = self.company_id.id
            vals['name'] = self.partner_id.name
            os = task.create(vals)
        for line in self.order_line:
            #linha['product_id'] = line.product_id.id
            #linha['price_unit'] = line.price_unit
            #linha['quantity'] = line.quantity
            #vals = {'material_ids': [(0, 0, linha)]}
            linha.append(
                (0, 0, {
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
            })
            )
            task_sale = {'material_ids':linha}
            #vals['material_ids'] = linha
            os.write(task_sale)
            linha = []
        #default_sale_order = {'material_ids': linha}

        msg_task = u'Criado OS de instalação número: %s' % (os.code)
        self.message_post(body=_(msg_task))
        return vals






