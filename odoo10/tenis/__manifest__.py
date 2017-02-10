# -*- coding: utf-8 -*-
{
    'name': "Flores Ranking",

    'summary': """
        Controle do Ranqueamento do Tenis do Clube Floresta""",

    'description': """
        Controla jogos e ranking do Tenis
    """,

    'author': "Carlos Silveira",
    'website': "http://www.atsti.com.br",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Esporte',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}