# -*- coding: utf-8 -*-
{
    'name': 'CRM_Product',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'ATS Myplace',
    'description': """
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['br_crm','hr','project'],
    'data': [
        'security/ir.model.access.csv',
        #'security/crm_productsite_security.xml',
        'views/crm_lead_view.xml',
        'views/crm_productsite_view.xml',
        'views/boasvindas_email_template.xml',
        'report/crm_sale_report_views.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
