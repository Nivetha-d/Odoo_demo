from datetime import timedelta
from odoo import api, fields, models

class ProdExt(models.Model):
    _inherit = "product.template"

    warranty = fields.Integer(string="Warranty Duration")
    warranty_type = fields.Selection(
        [
            ("day", "Day(s)"),
            ("week", "Week(s)"),
            ("month", "Month(s)"),
            ("year", "Year(s)"),
        ],
        required=True,
        default="day",
    )




































    #
    # stock_quant_ids = fields.One2many(
    #     'stock.quant', 'product_tmpl_id', string='Stock Quants',
    #
    #     help='Stock Quants related to this product template')
    #
    # expiration_date = fields.Datetime(
    #     string="Warranty Expiration Date", compute='_compute_expiration_date', store=True)
    #
    # @api.model
    # def _send_warranty_expiration_notification(self):
    #     # Find product templates with warranty about to expire
    #     print('anil')
    #     templates_to_notify = self.search([
    #         ('warranty', '>', 0),
    #         ('expiration_date', '<=', fields.Datetime.now() + timedelta(days=30)),
    #     ])
    #
    #     # Trigger mail for each template
    #     for template in templates_to_notify:
    #         template.message_post(
    #             body='The warranty is about to expire within 90 days.',
    #             subject='Warranty Expiration Notification',
    #             subtype_id=self.env.ref('mail.mt_comment').id)
    #
    # @api.depends('warranty', 'period', 'stock_quant_ids.inventory_date')
    # def _compute_expiration_date(self):
    #     for product_template in self:
    #         if product_template.warranty and product_template.stock_quant_ids:
    #             inventory_dates = [
    #                 fields.Datetime.from_string(date) for date in product_template.stock_quant_ids.mapped('inventory_date') if date]
    #
    #             if inventory_dates:
    #                 latest_inventory_date = max(inventory_dates)
    #
    #                 if product_template.period == 'month':
    #                     delta = timedelta(days=30)  # assuming 30 days in a month
    #                 else:
    #                     delta = timedelta(days=365)  # assuming 365 days in a year
    #
    #                 expiration_date = latest_inventory_date + timedelta(
    #                     days=product_template.warranty * delta.days)
    #
    #                 product_template.expiration_date = expiration_date
    #
    # def schedule_warranty_expiration_notification(self):
    #     # Schedule the cron job to execute the notification function
    #     # You can customize the interval based on your needs
    #     self.env['ir.cron'].sudo().create({
    #         'name': 'Send Warranty Expiration Notification',
    #         'model_id': self.env.ref('product_ext.model_prodext').id,
    #         'state': 'code',
    #         'code': 'model._send_warranty_expiration_notification()',
    #         'interval_number': 1,
    #         'interval_type': 'days',
    #         'numbercall': -1,
    #     })
