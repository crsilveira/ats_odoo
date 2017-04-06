# -*- coding: utf-8 -*-
{
    'name': "project_issue_myplace",

    'summary': """
        costumizacao Myplace atendimento""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project_issue','base', 'br_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_issue_view.xml',
        'views/res_partner_view.xml',
        'views/email_template_crm_claim.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}