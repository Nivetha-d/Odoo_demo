from odoo import api, fields, models

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    create_uid = fields.Char(compute='click')


    @api.model
    def click(self):
        self.create_uid = self.env.user.name
