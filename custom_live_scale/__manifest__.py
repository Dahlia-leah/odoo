{
    'name': 'Live Scale Weight Display',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Fetch and display live scale weight and unit from an API',
    'depends': ['web'],
    'data': [
        'views/live_scale_view.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_live_scale/static/src/js/live_scale.js',
        ],
    },
    'application': True,
    'installable': True,
}
