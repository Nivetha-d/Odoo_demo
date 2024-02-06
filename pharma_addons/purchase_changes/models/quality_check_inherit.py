from odoo import fields, api, models

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    location_id = fields.Many2one('stock.location', string='Destination Location',compute='_compute_location_id',store=True, help='Select the location where the product goes after quality check.')

    # @api.depends('picking_id', 'product_id')
    # def _compute_location_id(self):
    #     for quality_check in self:
    #         location_id = False
    #
    #         if quality_check.picking_id and quality_check.product_id:
    #             picking = quality_check.picking_id
    #             product = quality_check.product_id
    #
    #             # Find the related move in the picking for the specified product
    #             move = picking.move_ids.filtered(lambda m: m.product_id == product)
    #
    #             if move:
    #                 location_id = move.location_dest_id.id
    #
    #         quality_check.location_id = location_id

    @api.depends('picking_id', 'product_id', 'quality_state')
    def _compute_location_id(self):
        for quality_check in self:
            location_id = False

            if quality_check.quality_state in ['pass', 'fail']:
                if quality_check.picking_id and quality_check.product_id:
                    picking = quality_check.picking_id
                    product = quality_check.product_id

                    # Find the related move in the picking for the specified product
                    move = picking.move_ids.filtered(lambda m: m.product_id == product)

                    if move:
                        if quality_check.quality_state == 'pass':
                            location_id = self.env['stock.location'].search([('is_retest', '=', True)]).id
                        elif quality_check.quality_state == 'fail':
                            location_id = self.env['stock.location'].search([('is_blocked', '=', True)]).id

            quality_check.location_id = location_id

    def do_fail(self):
        super(QualityCheck, self).do_fail()

    def do_pass(self):
        super(QualityCheck, self).do_pass()
    # @api.depends('product_id')
    # def _compute_location_id(self):
    #     for quality_check in self:
    #         if quality_check.product_id:
    #             product = quality_check.product_id
    #             # Assuming product is stored in a specific location, adjust this logic accordingly
    #             location_id = product.product_tmpl_id.property_stock_inventory.id
    #         else:
    #             location_id = False
    #
    #         quality_check.location_id = location_id
    #         print(quality_check.location_id)




