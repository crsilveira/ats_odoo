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
            for record in self:
                record.active = not record.active
            self.date_end = fields.Date.context_today(self)
            self.partner_id.active = False
            for contact in self.partner_id.parent_id:
                contact.active = False
        else:
            raise UserError('Você não tem permissão para inativar um contrato')




