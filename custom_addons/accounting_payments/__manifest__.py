{
    'name': 'Accounting Payments',
    'summary': 'Importing payment records in txt format',
    'sequence': -100,
    'author':'Nivetha',
    'version': '1.0',
    'depends': ['base','account'],
    'data': [
       'security/ir.model.access.csv',
        'views/payment_wizard_view.xml',
        'views/payment_files.xml',
        'views/payment_button.xml',
        'views/account_invoice.xml',

        'views/payment_import_menu.xml',


    ],

# 'assets': {
#    'web.assets_backend': [
#        'accounting_payments/static/src/js/custom_button.js',
#        'accounting_payments/static/src/xml/custom_button_view.xml',
#    ]
# },

    'installable': True,
    'license':'LGPL-3'

}