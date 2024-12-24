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
        'views/device_views.xml',
        'views/connection_views.xml.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
