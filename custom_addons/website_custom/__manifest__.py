
{
    'name': 'Custom Website Menu',
    'version': '17.0.0.0.0',
    'category': 'Website',
    'author': 'Nivetha',
    'sequence': -100,
    'depends': ['website','mail'],
    'data': [

        'views/website_menu.xml',
        'views/signup_template.xml'
    ],
    'installable': True,
    'module_type': 'official',
    'license': 'LGPL-3'

}