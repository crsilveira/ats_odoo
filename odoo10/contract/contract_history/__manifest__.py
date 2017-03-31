# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts History',
    'description': 'Histórico dos reajustes de valores no contrato',
    'version': '10.0.1.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Carlos,"
              "ATS,"
              "",
    'website': '',
    'depends': ['contract'],
    'data': [
        'views/contract_view.xml',
    ],
    'installable': True,
}
