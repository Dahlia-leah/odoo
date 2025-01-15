{
    'name': 'Custom Helpdesk Enhancements',
    'version': '1.0',
    'license': 'LGPL-3',
    'summary': 'Filter helpdesk team members and auto-create tasks for tickets',
    'depends': ['helpdesk', 'project',  'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_team_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}