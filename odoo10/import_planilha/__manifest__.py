# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos R Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Importar Planilhas',
    'version': '1.0',
    'author': 'ATS Solucoes',
    'description': '''Import csv files''',
    'website': 'http://www.atsti.com.br/',
    'category': 'Contract Management',
    'depends': [
        'base', 'analytic',
    ],
    'data':  [
        'views/import_product_contract_view.xml',
        'views/import_linha_aparelho_view.xml',
        'views/import_conta_view.xml',
        #'security/security_groups.xml',
        #'security/ir.model.access.csv',
    ],
    'installable': True,
    'images': [],

}

