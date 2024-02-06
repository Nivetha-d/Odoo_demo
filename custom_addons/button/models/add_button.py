from odoo import models, fields,api

class ShowButton(models.Model):
    _name = 'show.button'

    check = fields.Boolean(string="Contract")
    partner = fields.Many2one('res.partner',string="Partner")
    product_name = fields.Many2one('product.template', string="Product")

    @api.onchange('partner')
    def onchange_partner(self):
        if self.partner:
            self.check = True

    def action_confirm(self):
        if self.partner and self.product_name:
            purchase_order = self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                # Add other necessary fields for the purchase order
            })

            purchase_order_line = self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': self.product_name.product_variant_id.id,
                'product_qty': 1,  # You may adjust the quantity as needed
                # Add other necessary fields for the purchase order line
            })

            # You can customize this part based on your specific requirements

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': purchase_order.id,
                'view_mode': 'form',
                'view_id': False,
                'target': 'current',
            }
        else:
            # Handle the case where either partner or product is not selected
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'Please select both a partner and a product before confirming.',
                }
            }




