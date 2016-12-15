# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    contract_id = fields.Many2one("account.analytic.account", string="Contrato", readonly=True)
    mobile = fields.Boolean("Celular")