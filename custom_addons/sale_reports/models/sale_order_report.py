from odoo import models, api

class CustomSaleReport(models.Model):
    _inherit = 'sale.order'