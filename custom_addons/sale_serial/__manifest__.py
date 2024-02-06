{
    'name' : 'Sale order serial.no',
    'version' : '2.0',
    'author': 'Nivetha',
    'summary': 'Custom select the serial number for sale order',
    'sequence': -100,
    'depends': ['base','sale','stock'],
    'data': [
        'views/sale_serial.xml'
    ],

    'installable': True,

    'module_type': 'official',
    'license': 'LGPL-3'
}