{
    'name': 'Devices',
    'version': '1.0',
    'category': 'Inventory',  
    'summary': 'Manage devices in the system',
    'description': """
        This module helps you manage devices in the Odoo system.
    """,
    'depends': ['base', 'stock'],  
    'data': [
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
