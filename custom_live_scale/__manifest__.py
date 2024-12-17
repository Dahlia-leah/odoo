{
    'name': 'Custom Live Scale',
    'version': '1.0',
    'summary': 'Module for Live Scale Integration',
    'category': 'Custom',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/live_scale_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_live_scale/static/src/js/live_scale.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
