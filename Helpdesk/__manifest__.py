{
    'name': 'Custom Helpdesk',
    'version': '1.0',
    'category': 'Services/Helpdesk',
    'license': 'LGPL-3',
    'summary': 'Custom Helpdesk module with team-based ticket assignment and task creation',
    'description': """
        This module extends the Helpdesk functionality:
        - Allows creation of Helpdesk Teams
        - Restricts ticket assignment to team members
        - Automatically creates tasks for new tickets
    """,
    'depends': ['base', 'helpdesk', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/project_task_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

