{
    'name' : 'product ext',
    'version' : '2.0',
    'author': 'bellamkonda anli',
    'summary': 'customer interest',
    'sequence': 10,
    'depends': ['product','stock'],
    'data': [
        'data/cron.xml',
        'data/send_mail.xml',
        'views/products.xml',
        'views/stock_production_lot.xml'

    ],

    'installable': True,

    'module_type': 'official',
    'license': 'LGPL-3'
}