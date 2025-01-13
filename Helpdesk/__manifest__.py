{
    'name': 'Custom Helpdesk Enhancements',
    'version': '1.0',
    'license': 'LGPL-3',
    'summary': 'Filter helpdesk team members and auto-create tasks for tickets',
    'author': 'Your Name',
    'depends': ['helpdesk', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
