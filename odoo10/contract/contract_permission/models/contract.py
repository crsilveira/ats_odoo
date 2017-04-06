# -*- coding: utf-8 -*-
from odoo import api,fields, models, _
from odoo.exceptions import UserError
from datetime import datetime

#from odoo.addons.br_boleto.boleto.document import Boleto

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    date_end = fields.Datetime(string='Data de encerramento')

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        user_uid = self.env['res.users'].browse(self._uid)
        if any(line.name == 'Conselheiro' for line in user_uid.groups_id):
            vals = {}
            for record in self:
                record.active = not record.active
            if self.active:
                self.date_end = False
            else:
                self.date_end = fields.Date.context_today(self)

            partner = self.env['res.partner'].browse(self.partner_id.id)
            vals['active'] = self.active
            partner.write(vals)
            if self.partner_id.child_ids:
                for contact in self.partner_id.child_ids:
                    contact = self.env['res.partner'].browse(contact.id)
                    contact.write(vals)
            else:
                res_partner = self.env['res.partner'].search([
                    ('parent_id','=',self.partner_id.id),
                    ('active','=',False)])
                for contact in res_partner:
                    contact = self.env['res.partner'].browse(contact.id)
                    contact.write(vals)
        else:
            raise UserError('Você não tem permissão para inativar um contrato')




