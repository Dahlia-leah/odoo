{
    'name': 'Stock Picking Report',
    'version': '1.0',
    'summary': 'Add scale integration and reporting to stock picking',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
        'reports/stock_picking_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}