{
    'name': 'Stock Picking Report',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'summary': 'Add a button to fetch weight from IoT device and print stock picking reports.',
    'depends': ['stock', 'iot'],
    'data': [
        'views/stock_picking_views.xml',
        'reports/stock_picking_report_template.xml',
    ],'assets': {
        'web.assets_backend': [
            'your_module/static/src/js/live_weight_bus.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
