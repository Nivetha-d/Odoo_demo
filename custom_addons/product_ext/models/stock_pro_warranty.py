from dateutil.relativedelta import relativedelta

from odoo import api, fields, models



DELTA_TYPES = ("day", "week", "month", "year")


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    warranty_exp_date = fields.Date(string="Warranty Expiration Date")

    def _get_warranty_exp_date(self, start_date=None):
        if not start_date:
            start_date = fields.Date.context_today(self)
        elif hasattr(start_date, "astimezone"):
            # Datetime object, convert to date
            start_date = fields.Date.context_today(self, timestamp=start_date)
        delta_type = self.product_id.product_tmpl_id.warranty_type
        duration = self.product_id.product_tmpl_id.warranty
        if not duration or delta_type not in DELTA_TYPES:
            return False
        return start_date + relativedelta(**{f"{delta_type}s": duration})

    @api.onchange("product_id")
    def _onchange_product_id(self):

        self.warranty_exp_date = self._get_warranty_exp_date()

    @api.model
    def test_cron(self):
        current_datetime = fields.Datetime.now()
        two_days_before = current_datetime + relativedelta(days=2)
        print(two_days_before)
        lots_to_notify = self.env['stock.lot'].search([
            ('warranty_exp_date', '=', two_days_before.strftime('%Y-%m-%d')),

        ])
        print(lots_to_notify)
        for lot in lots_to_notify:
            # Compose the email body
            email_body = f"Product {lot.product_id.name} is going to expire in two days."
            # Send the email
            print(email_body)
            self.send_email(email_body)


    def send_email(self, body):
        # Create an instance of the Mail class
        mail_obj = self.env['mail.mail']

        # Compose the email
        email_values = {
            'subject': "Product Expiration Mail",
            'body_html': body,
            'email_to': "nivethanivetha95639@gmail.com",
        }

        # Send the email
        mail_id = mail_obj.create(email_values)
        mail_id.send()





