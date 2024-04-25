{
    'name': 'Sale order reports',
    'summary': 'Customising the report in sales',
    'sequence': -100,
    'author':'Nivetha',
    'version': '1.0',
    'depends': ['base','sale','l10n_din5008','web'],
    'data': [
        'report/sale_quotation.xml',
        'report/sale_invoices.xml',
        'report/sale_delivery.xml',
        'views/sale_quotation_content.xml',

    ],


    'installable': True,
    'license':'LGPL-3'

}