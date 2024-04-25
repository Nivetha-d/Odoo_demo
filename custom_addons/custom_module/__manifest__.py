# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://kanakinfosystems.com>).
{
    "name": "Custom Module",
    "version": "17.0.1.0",
    "category": "",
    'license': 'OPL-1',
    "summary": " ",
    "discription": " ",
    "depends": ["sale_management"],
    "author": "Kanak Infosystems LLP",
    "website": "www.kanakinfosystems.com",
    "data": [
        'views/sale_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_module/static/src/js/list_view_button.js',
            'custom_module/static/src/xml/list_view_button.xml',
        ]
    },
    'sequence': 1,
    'installable': True,
    'application': True,
}
