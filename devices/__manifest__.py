{
    'name': 'Real Estate Advertisement',
    'version': '1.0',
    'summary': 'Module for managing real estate advertisements',
    'description': """
        This module allows users to manage real estate advertisements.
    """,
    'author': 'Your Name',
    'category': 'Real Estate',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/real_estate_view.xml',
    ],
    'installable': True,
    'application': True,
}