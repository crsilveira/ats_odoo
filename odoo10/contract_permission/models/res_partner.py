# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def toggle_active(self):
        if not self.contract_ids:
            for record in self:
                record.active = not record.active
        else:
            raise UserError('Cliente tem contratos, inative-os primeiro.')