# -*- coding: utf-8 -*-
{
    'name': "purchase_changes",

    'version': '1.0',
    'summary': 'Purchase Requisition ',
    'sequence': 120,
    'description': """

    """,

    'depends': ['base', 'purchase', 'stock', 'quality_control', 'sale','product','quality'],

    'data': [

        'security/ir.model.access.csv',
        'views/new_button.xml',

        'views/purchase_req_lines.xml',
        'views/puchase_req.xml',
        'views/GroupsAcess.xml',
        'data/ir_cron.xml'

    ],

    'installable': True,
    'application': True,

    'license': 'LGPL-3',

}
