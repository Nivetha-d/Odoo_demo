from odoo import http
from odoo.http import request

class FlightTicket(http.Controller):

    @http.route('/flight/ticket', type="http", website=True, auth='public')
    def flight_ticket(self, **kw):
        fields = {
            'origin_options': ['JFK', 'DEL', 'SYD', 'BOM', 'BNE', 'BLR'],
            'destination_options': ['JFK', 'DEL', 'SYD', 'LHR', 'CDG', 'DOH', 'SIN'],
            'cabin_options': ['Economy', 'Business', 'First']
        }
        return request.render('flight.flight_ticket_page_main',fields)


