# -*- encoding: utf-8 -*-
###############################################################################
# #                                                                           #
# Telefonia for Odoo #                                                        #
# Copyright (C) 2016 ATS Solucoes (<http://www.atsti.com.brt>). #             #
# Contributors                                                                #
# Carlos R. Silveira, carlos@atsti.com.br, #                                  #
# #                                                                           #
# This program is free software: you can redistribute it and/or modify #      #
# it under the terms of the GNU Affero General Public License as #            #
# published by the Free Software Foundation, either version 3 of the #        #
# License, or (at your option) any later version. #                           #
# #                                                                           #
# This program is distributed in the hope that it will be useful, #           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of #            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the #              #
# GNU Affero General Public License for more details. #                       #
# #                                                                           #
# You should have received a copy of the GNU Affero General Public License #  #
# along with this program. If not, see <http://www.gnu.org/licenses/>. #      #
# #                                                                           #
###############################################################################
###############################################################################
# Telefonia is an Openobject module wich enable management for  Mobile        #
# Company                                                                     #
###############################################################################
{
    'name': 'Telefonia',
    'version': '10.0.0.1.0',
    'category': 'Contract',
    'summary': '',
    'author': 'ATS',
    'license': 'AGPL-3',
    'depends': ['product', 'contract'],
    'data': [
        'views/product_view.xml',
        #'security/ir.model.access.csv'
    ],
    'installable': True,
}