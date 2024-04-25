from odoo import api, fields, models
from collections import defaultdict
from datetime import timedelta
from operator import itemgetter
from re import findall as regex_findall

from odoo import _, api, Command, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import clean_context, OrderedSet, groupby

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    serial_no = fields.Many2many(
        'stock.lot',
        'stock_move_line_lot_rel',
        'stock_move_line_id',
        'lot_id',
        string='Lot/Serial Numbers',
        domain="[('product_id', '=', product_id)]",
        check_company=True,
    )





class Stockmove(models.Model):

    _inherit = 'stock.move'

    def _update_reserved_quantity(self, need, location_id, quant_ids=None, lot_id=None, package_id=None, owner_id=None,
                                  strict=True):
        """ Create or update move lines and reserves quantity from quants
            Expects the need (qty to reserve) and location_id to reserve from.
            `quant_ids` can be passed as an optimization since no search on the database
            is performed and reservation is done on the passed quants set
        """
        self.ensure_one()
        if quant_ids is None:
            quant_ids = self.env['stock.quant']
        if not lot_id:
            lot_id = self.env['stock.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']

        quants = quant_ids._get_reserve_quantity(
            self.product_id, location_id, need, product_packaging_id=self.product_packaging_id,
            uom_id=self.product_uom, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)

        taken_quantity = 0
        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # Find a candidate move line to update or create a new one.
        for reserved_quant, quantity in quants:
            taken_quantity += quantity
            to_update = next(
                (line for line in self.move_line_ids if line._reservation_is_updatable(quantity, reserved_quant)),
                False)
            if to_update:
                uom_quantity = self.product_id.uom_id._compute_quantity(quantity, to_update.product_uom_id,
                                                                        rounding_method='HALF-UP')
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                uom_quantity_back_to_product_uom = to_update.product_uom_id._compute_quantity(uom_quantity,
                                                                                              self.product_id.uom_id,
                                                                                              rounding_method='HALF-UP')
            if to_update and float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                to_update.with_context(reserved_quant=reserved_quant).quantity += uom_quantity
            else:
                if self.product_id.tracking == 'serial':
                    vals_list = self._add_serial_move_line_to_vals_list(reserved_quant, quantity)
                    # if vals_list:
                    #     self.env['stock.move.line'].with_context(reserved_quant=reserved_quant).create(vals_list)
                    if vals_list:
                        sale_order_line = self.sale_line_id
                        selected_serial_nos = sale_order_line.serial_no.ids

                        filtered_quants = self.env['stock.quant'].search([
                            ('product_id', '=', self.product_id.id),
                            ('lot_id', 'in', selected_serial_nos),
                            # ('location_id', '=', location_id),
                            ('quantity', '>', 0),
                        ])

                        for quant in filtered_quants:
                            move_line_vals = vals_list[0].copy()
                            move_line_vals.update({'lot_id': quant.lot_id.id})
                            self.env['stock.move.line'].with_context(reserved_quant=quant).create(move_line_vals)
                        break

                else:
                    self.env['stock.move.line'].with_context(reserved_quant=reserved_quant).create(
                        self._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant))
        return taken_quantity


