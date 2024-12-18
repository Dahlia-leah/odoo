# -*- coding: utf-8 -*-
{
    'name': "GKIST e-invoice",

    'summary': """
        """,
    'description': """
     Egypt E-Invoice System
    """,
    'author': "G K I S T",
    'website': "http://gkist-eg.odoo.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account'],

    'data': [
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
