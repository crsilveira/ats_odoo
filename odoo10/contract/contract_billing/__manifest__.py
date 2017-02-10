# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts Automatic Billing',
    'version': '10.0.1.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Carlos,"
              "ATS,"
              "",
    'website': '',
    'depends': ['contract','contract_invoice', 'br_boleto'],
    'data': [
        #'security/ir.model.access.csv',
        #'data/contract_cron.xml',
        'views/contract_view.xml',
        'views/email_erro_fatura.xml',
        'views/email_einvoice_template.xml',
        #'views/account_invoice_view.xml',
    ],
    'installable': True,
}
