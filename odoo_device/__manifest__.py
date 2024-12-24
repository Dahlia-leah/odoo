{
    'name': 'Odoo Device',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Manage Devices in the System',
    'description': """
        This module helps you manage devices and their connections.
    """,
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/connection_views.xml',
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
