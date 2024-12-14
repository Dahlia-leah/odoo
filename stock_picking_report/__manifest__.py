{
    'name': 'Stock Picking Report',
    'version': '1.0',
    'license': 'LGPL-3',  # Specify the license here
    'category': 'Inventory',
    'summary': 'Add a button to print reports in stock picking forms',
    'depends': ['stock', 'iot'],  # This module depends on the stock module
    'data': [
        'views/stock_picking_views.xml',  # View modifications (e.g., form view with JS)
        'reports/stock_picking_report_template.xml',  # Report template
    ],
    'installable': True,
}
