from odoo import api, fields, models

class WebsiteMenu(models.Model):
    _inherit = ['mail.thread','website.menu']
    _name = 'website.menu'

    name = fields.Char(string='Name')
    email = fields.Char(string='Email')

