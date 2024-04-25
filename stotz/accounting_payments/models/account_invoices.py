from odoo import models, api

class CustomAccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        if self._name == 'account.move':
            if vals.get('move_type') == 'out_invoice':
                if vals.get('state') != 'draft':
                    sequence = self.env['ir.sequence'].search([('code', '=', 'custom.account.move.sequence')], limit=1)
                    if not sequence:
                        sequence = self.env['ir.sequence'].create({
                            'name': 'Custom Account Move Sequence',
                            'code': 'custom.account.move.sequence',
                            'padding': 3,  # Adjust the padding as needed
                            'number_increment': 1,  # Adjust the increment as needed
                            'implementation': 'standard',
                            'prefix': '40044',
                        })
                    vals['name'] = sequence.next_by_id().zfill(3)
        return super(CustomAccountMove, self).create(vals)



