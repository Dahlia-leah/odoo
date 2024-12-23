{
    'name': 'Devices',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Manage devices in the system',
    'description': """
        This module helps you manage devices in the Odoo system.
    """,
    'depends': ['point_of_sale'],  
    'data': [
        'views/device_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
