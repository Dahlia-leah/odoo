{
    'name': 'Live Scale Integration',
    'version': '1.0',
    'category': 'Tools',
    'license': 'LGPL-3',
    'summary': 'Integration with Live Scale for Weight Data',
    'description': """
        A custom Odoo module to integrate with a live scale via an API, exposing data on the Odoo system.
    """,

    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/live_scale_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}
