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

        'views/account_invoice.xml',

        'views/payment_import_menu.xml',


    ],



    'installable': True,
    'license':'LGPL-3'

}