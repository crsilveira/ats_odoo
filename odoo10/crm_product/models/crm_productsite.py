 #-*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CrmProductsite(models.Model):
    _name = 'crm.productsite'
    _description = "Product Site"

    name = fields.Char('Product Name', required=True)
    active = fields.Boolean('Active', default=True)

