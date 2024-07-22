{
    'name': 'Flight Ticket Details',
    'summary': 'Fetching flight ticket details using API',
    'sequence': -100,
    'author':'Nivetha',
    'version': '1.0',
    'depends': ['base','website','account'],
    'data': [
        'views/flight_ticket_page.xml',


    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         'flight/static/js/flight_search.js',  # Add your JS file here
    #
    #     ],
    # },



    'installable': True,
    'license':'LGPL-3'

}