# -*- coding: utf-8 -*-
{
    'name': "purchase_changes",

    'version': '1.0',
    'summary': 'Purchase Requisition ',
    'sequence': 10,
    'description': """

    """,

    'depends': ['base', 'purchase','stock','quality_control','sale','account'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'report/invoice_inherit.xml',
        'views/purchase_req_lines.xml',
        'views/puchase_req.xml',
        'views/GroupsAcess.xml',
        'views/invoice_report_inherit.xml',
        'views/quality_check_inherit.xml'
    ],

    'installable': True,
    'application': True,

    'license': 'LGPL-3',


}
