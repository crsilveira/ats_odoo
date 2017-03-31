# -*- coding: utf-8 -*-

###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Domatix (<www.domatix.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Contract Invoice',
    'summary': 'Finance information to contracts and their invoices',
    'version': '10.0.1.1.0',
    'category': 'Contract Management',
    'author': 'crsilveira@gmail.com, Odoo Community Association (OCA)',
    'website': 'http://www.atsti.com.br',
    'depends': [
        'account',
        'br_base',
        'analytic',
        'br_account_payment'],
    'license': 'AGPL-3',
    'data': [
        'views/contract_view.xml',
        'views/partner_view.xml',
        #'security/ir.model.access.csv',
    ],
    'test': ['test/contract_payment_mode.yml'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
}
