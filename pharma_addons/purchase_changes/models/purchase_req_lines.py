from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, get_lang
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class TestQuality(models.Model):
    _inherit = 'stock.picking'

    def check_quality(self):
        x = super(TestQuality,self).check_quality()
        print('newwwww', x)
        return x

class PurchaseReqProductLinesRFQ(models.Model):
    _name = 'pur.req.lines'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char('Name', required=True)
    product_uom_qty = fields.Float('Quantity', default=1)
    price_unit = fields.Float('Unit Price', )
    pur_id = fields.Many2one('purchase.newchanges')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    requisition_action = fields.Many2one('stock.picking.type', string='Requisition Action')

    vendor_name = fields.Many2one('res.partner', string='Vendor Name',
                                  domain=[('is_company', '=', True),
                                          ('invoice_ids.name', '!=',
                                           False)])


    @api.onchange('product_id')
    def prod_onchange_get_order_id(self):
        for rec in self:
            self.price_unit = self.price_unit
            self.uom_id = rec.product_id.uom_id.id
            self.name = rec.product_id.name









class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'product_uom', 'company_id')
    def _compute_price_unit_and_date_planned_and_name(self):
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            params = {'order_id': line.order_id}
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date() or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params)

            if seller or not line.date_planned:
                line.date_planned = line._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            # If not seller, use the standard price. It needs a proper currency conversion.
            if not seller:
                unavailable_seller = line.product_id.seller_ids.filtered(
                    lambda s: s.partner_id == line.order_id.partner_id)
                if not unavailable_seller and line.price_unit and line.product_uom == line._origin.product_uom:
                    # Avoid to modify the price unit if there is no price list for this partner and
                    # the line has already one to avoid to override unit price set manually.
                    continue
                po_line_uom = line.product_uom or line.product_id.uom_po_id
                price_unit = line.env['account.tax']._fix_tax_included_price_company(
                    line.product_id.uom_id._compute_price(line.product_id.standard_price, po_line_uom),
                    line.product_id.supplier_taxes_id,
                    line.taxes_id,
                    line.company_id,
                )
                price_unit = line.product_id.cost_currency_id._convert(
                    price_unit,
                    line.currency_id,
                    line.company_id,
                    line.date_order or fields.Date.context_today(line),
                    False
                )
                line.price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                               self.env[
                                                                                   'decimal.precision'].precision_get(
                                                                                   'Product Price')))
                continue

            price_unit = line.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                                 line.product_id.supplier_taxes_id,
                                                                                 line.taxes_id,
                                                                                 line.company_id) if seller else 0.0
            price_unit = seller.currency_id._convert(price_unit, line.currency_id, line.company_id,
                                                     line.date_order or fields.Date.context_today(line), False)
            price_unit = float_round(price_unit, precision_digits=max(line.currency_id.decimal_places,
                                                                      self.env['decimal.precision'].precision_get(
                                                                          'Product Price')))
            # line.price_unit = seller.product_uom._compute_price(price_unit, line.product_uom)
            line.discount = seller.discount or 0.0

            # record product names to avoid resetting custom descriptions
            default_names = []
            vendors = line.product_id._prepare_sellers({})
            for vendor in vendors:
                product_ctx = {'seller_id': vendor.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                default_names.append(line._get_product_purchase_description(line.product_id.with_context(product_ctx)))
            if not line.name or line.name in default_names:
                product_ctx = {'seller_id': seller.id, 'lang': get_lang(line.env, line.partner_id.lang).code}
                line.name = line._get_product_purchase_description(line.product_id.with_context(product_ctx))


class LocationQuality(models.Model):
    _inherit = 'quality.point'

    src_location = fields.Many2one('stock.location', string='Source Location')
    destination_location = fields.Many2one('stock.location', string='Destination Location')


class QualityCheckWizardNew(models.TransientModel):
    _inherit = 'quality.check.wizard'

    stock_picking = fields.Many2one('stock.picking')

    def do_pass(self):
        active_id = self._context.get('stock_picking')
        print(active_id)
        # active_id = self._context.get('params').get('id',False)
        stock_picking_id = self.env['stock.picking'].browse(active_id)
        print(active_id, 'aaaaaaaaaaaaa')
        self.stock_picking = stock_picking_id.id
        if self.stock_picking.id:
            res = super(QualityCheckWizardNew, self).do_pass()
            print('resssssssssssssssssssssssssssssssssssssss', res)
            stock_picking_id.location_dest_id = self.env['stock.location'].search([('is_unrestricted', '=', True)]).id
            pass
        else:
            raise ValidationError('Please refresh page and try again')

    def do_fail(self):
        active_id = self._context.get('stock_picking')
        print(active_id)
        # active_id = self._context.get('params').get('id',False)
        stock_picking_id = self.env['stock.picking'].browse(active_id)
        # print(active_id, 'aaaaaaaaaaaaa')
        self.stock_picking = stock_picking_id.id
        if self.stock_picking.id:
            res = super(QualityCheckWizardNew, self).do_fail()
            print('resssssssssssssssssssssssssssssssssssssss', res)
            stock_picking_id.location_dest_id = self.env['stock.location'].search([('is_restricted', '=', True)]).id
            pass
        else:
            raise ValidationError('Please refresh page and try again')



class CheckQualityInherit(models.Model):
    _inherit = 'stock.picking'

    def check_quality(self):
        x = super(CheckQualityInherit, self).check_quality()

        if isinstance(x, dict) and 'context' in x:

            x['context'].update({
                'stock_picking': self.id
            })

            print(x)
            return x




class StockingLocationNew(models.Model):
    _inherit = "stock.location"

    is_restricted = fields.Boolean(string='Is restricted')
    is_unrestricted = fields.Boolean(string='Is Unrestricted')


# class CheckExpiry(models.Model):
#     _inherit = "purchase.order"
#
#     expiry=fields.Date("Expiry Date",compute="_compute_expiry_date")
#
#     def _compute_expiry_date(self):
#         for order in self:
#             # Get the current date
#             current_date = fields.Date.today()
#
#             # Calculate the expiry date by adding 6 months to the current date
#             expiry_date = (current_date + timedelta(days=6*30)).strftime('%Y-%m-%d')
#
#             # Assign the calculated expiry date to the field
#             order.expiry = expiry_date


class ProductMove(models.Model):
    _name = "product.move"
    _description = "Product Move"


#     _inherit = ["stock.picking"]
#
#     name = fields.Char("Name")
#     location_id = fields.Many2one("stock.location", "Current Location")
#     expiry_date = fields.Date("Expiry Date")
#     product_category = fields.Many2one("product.category", "Product Category")
#
#     def move_to_reanalysis(self):
#         # Identify products that are 6 months or more past their expiry date
#         # expired_products = self.search([('expiry_date', '<=', fields.Date.today() - timedelta(days=6 * 30))])
#         # expired_products = self.search([('expiry_date', '<=', fields.Date.today() - timedelta(days=6 * 30))])
#         expired_products = self.env['purchase.order'].search([('expiry','=','07/21/2024')])
#         print(expired_products)
#is_restricted
#         # Move expired products to the Reanalysis location
#         # reanalysis_location = self.env['stock.location'].search([('name', '=', 'Reanalysis')], limit=1)
#         reanalysis_location = self.env['stock.location'].search([('is_reanalysis', '=', True)], limit=1)
#         excipient_category = self.env['product.category'].search([('name', '=', 'Exipient')], limit=1)
#         print(self.location_id, self.product_category)
#
#
#         # for product in expired_products:
#         #     product.write({
#         #         'location_id': reanalysis_location.id if reanalysis_location else False,
#         #         'product_category': excipient_category.id if excipient_category else False,
#         #     })


class Reanalysis(models.Model):
    _inherit = "stock.location"

    is_reanalysis = fields.Boolean(string='Is Reanalysis')


#
# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     inward_date = fields.Date(string='Inward Date', help='Date when the products were received inward', default=fields.Date.context_today)
#
#     @api.onchange('state')
#     def _onchange_state(self):
#         if self.state == 'purchase':
#             self.inward_date = fields.Date.context_today(self)
#         else:
#             self.inward_date = False


#
# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     inward_date = fields.Date(string='Inward Date', help='Date when the products were received inward')

# @api.model
# def button_confirm(self):
#     res = super(PurchaseOrder, self).button_confirm()
#     if self.state == 'purchase':
#         self.write({'inward_date': fields.Date.context_today(self)})
#     return res


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     inward_date = fields.Date(
#         string='Inward Date',
#         related='purchase_order.inward_date',
#         store=True,
#         readonly=True
#     )
# # class ProductTemplate(models.Model):
# #     _inherit = 'product.template'
# #
# #     inward_date = fields.Date(string='Inward Date', store=True, readonly=True)
# #
# #     purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')


class productTemplateInherit(models.Model):
    _inherit = 'product.template'

    inward_date = fields.Datetime(string='Inward Date', readonly=True)
    expiry_date = fields.Datetime(string='Expiry Date')

    # def update_product_after_six_months(self):
    #     pass

    # @api.model
    # def update_product_after_six_months(self):
    #     six_months_ago = datetime.now() - timedelta(days=180)
    #     products_to_update = self.env['product.product'].search([('inward_date', '<=', six_months_ago)])
    #
    #     active_category_id = self.env.ref(
    #         'product.product_category_search_view').id
    #     exception_category_id = self.env.ref(
    #         'product.product_category_search_view').id
    #
    #     products_to_update.write({'categ_id': exception_category_id})
    #
    #     products_within_six_months = self.env['product.template'].search([('inward_date', '>', six_months_ago)])
    #     products_within_six_months.write({'categ_id': active_category_id})


# from odoo import models, fields, api
# #
# # from odoo import models, fields, api
# #
# from odoo import models, fields, api

#
# class CustomStockMove(models.Model):
#     _inherit = 'stock.move'
# #
# #     stock_check = fields.Many2one(comodel_name='stock.picking')
#     check_ids = fields.One2many('quality.check', 'picking_id', 'Checks')
#     picking_ids=fields.Many2one('stock.picking.batch')

    # class CustomStockMove(models.Model):
    #
    #     _inherit = 'stock.move'
    #
    #     check_ids = fields.One2many('quality.check', 'picking_id', 'Checks')
    #     picking_ids = fields.Many2one('stock.picking.batch')
    #     stock_check = fields.Many2one(comodel_name='stock.picking', string='Stock Picking')
    #     next_id=fields.Integer('ID',default=41)
    # quality_check_todo = fields.Boolean('Pending checks', compute='_compute_check')

    # def check_quality(self):
    #     print('Oringinal context', self.env.context)
    #     # picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
    #     new_context = dict(self.env.context)
    #     if 'form_view_ref' in new_context:
    #         del new_context       ['form_view_ref']
    #     print("Modified context:", new_context)
    #     picking_id = self.env['stock.picking'].search([('id', '=', 519)])
    #     # # check_ids = self.picking_ids.check_ids.filtered(lambda check: check.quality_state == 'none')
    #     print('picking_id', picking_id)
    #     if picking_id:
    #         return picking_id.check_quality().new_context
    #         return new_context




##working###
        # return {
            # # 'name': _('Quality Check'),
            # # 'type': 'ir.actions.act_window',
            # # 'view_mode': 'form',
            # # 'res_model': 'quality.check',
            # # 'target': 'current',
            # # 'res_id': self.check_ids.id,
            # 'id': 628,
            # 'type': 'ir.actions.act_window',
            # 'xml_id': 'quality_control.action_quality_check_wizard',
            # 'binding_type': 'action',
            # 'binding_view_types': 'list,form',
            # 'display_name': 'Quality Check',
            # 'view_id': False,
            # 'context': {'params': {'id': 523, 'cids': '1-2', 'menu_id': 222, 'action': 400, 'active_id': 173, 'model': 'stock.picking', 'view_type': 'form'},
            #             'active_id': 173, 'active_ids': [173], 'contact_display': 'partner_address', 'default_company_id': 1, 'lang': 'en_US', 'tz': 'Asia/Calcutta', 'uid': 2, 'allowed_company_ids': [1, 2], 'default_check_ids': [222], 'default_current_check_id': 222, 'default_qty_tested': 0.0, 'stock_picking': 523}, 'res_id': 0, 'res_model': 'quality.check.wizard', 'target': 'new', 'view_mode': 'form', 'mobile_view_mode': 'kanban', 'views': [(False, 'form')], 'limit': 80, 'groups_id': [], 'search_view_id': False, 'filter': False}
            #


###working
    # def check_quality(self):
    #     # purchase_line_id=self.env['stock.move'].browse(self.env.context['default_purchase_line_id'])
    #     print('move_line_ids', self.move_line_ids)
    #     print('Original context:', self.env.context)
    #     picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
    #     print(self.ids)
    #
    #     # picking_id = self.env['stock.picking'].search([('id')])
    #     print('picking_id', picking_id)
    #     print('picking_id.state:', picking_id.state)
    #
    #
    #     if picking_id:
    #         # Call the check_quality method on the picking_id
    #
    #         new_context = picking_id.check_quality()
    #
    #         new_context['context'].update({
    #             'stock_picking': picking_id.id
    #         })
    #
    #         print('1111', new_context)
    #         del new_context['context']['form_view_ref']
    #         print('22222', new_context)
    #
    #         # Return the modified context
    #         return new_context

    # def check_quality(self):
    #     print('Original context:', self.env.context)
    #
    #     # Check if the current record is a stock.picking or stock.move
    #     if 'default_picking_id' in self.env.context:
    #         picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
    #
    #         print('picking_id', picking_id)
    #         print('picking_id.state:', picking_id.state if picking_id else 'N/A')
    #
    #         if picking_id:
    #             # Check if the state is 'done' or 'cancel'
    #             if picking_id.state in ('done', 'cancel'):
    #                 # If state is 'done' or 'cancel', return an empty dictionary to make the button invisible
    #                 return {}
    #
    #             # Call the check_quality method on the picking_id
    #             new_context = picking_id.check_quality()
    #
    #             new_context['context'].update({
    #                 'stock_picking': picking_id.id
    #             })
    #
    #             print('1111', new_context)
    #             del new_context['context']['form_view_ref']
    #             print('22222', new_context)
    #
    #             # Return the modified context
    #             return new_context
    #
    #     # If the current record is a stock.move, return an empty dictionary to make the button invisible
    #     return {}


###Suprit
    # def check_quality(self):
    #     print('Original context:', self.env.context)
    #     picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
    #     print(self.ids)
    #
    #     print('picking_id', picking_id)
    #     print('picking_id.state:', picking_id.state)
    #
    #     if picking_id:
    #         # Call the check_quality method on the picking_id
    #         new_context = picking_id.check_quality()
    #
    #         new_context['context'].update({
    #             'stock_picking': picking_id.id
    #         })
    #
    #         print('1111', new_context)
    #         del new_context['context']['form_view_ref']
    #
    #         # Extract single check_id from the list of check_ids
    #         single_check_id = new_context['context'].get('default_check_ids', [])[0]  # Extract the first check_id
    #         print('single_check_id', single_check_id)
    #         quality_check_id = self.env['quality.check'].search([('id', '=', single_check_id)])
    #
    #         print('quality_check_id', quality_check_id)
    #
    #
    #         # print(self.env['stock.move.line'].search([()]))
    #
    #
    #         move_line_id = quality_check_id.move_line_id
    #         print('move_line_id', move_line_id)
    #         check_ids = move_line_id.check_ids
    #         print('check_ids', check_ids)
    #
    #
    #
    #         # Update the context with the single check_id
    #         new_context['context'].update({
    #             'default_check_ids': [single_check_id]  # Set the single check ID in the context
    #         })
    #
    #         print('22222', new_context)
    #
    #         # Return the modified context
    #         return new_context

    # def action_generate_next_window(self):
    #     quality_wizard_id = self.env.context.get('quality_wizard_id')
    #     if quality_wizard_id:
    #         quality_wizard = self.env['quality.check.wizard'].browse(quality_wizard_id)
    #         return quality_wizard.action_generate_next_window()
    #     return {'type': 'ir.actions.act_window_close'}

    # def check_quality(self):
    #     print('Original context:', self.env.context)
    #     picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
    #     print(self.ids)
    #
    #     print('picking_id', picking_id)
    #     print('picking_id.state:', picking_id.state)
    #
    #     if picking_id:
    #         # Call the check_quality method on the picking_id
    #         new_context = picking_id.check_quality()
    #
    #         new_context['context'].update({
    #             'stock_picking': picking_id.id
    #         })
    #
    #         print('1111', new_context)
    #         del new_context['context']['form_view_ref']
    #
    #         # Get the list of check_ids
    #         check_ids = new_context['context'].get('default_check_ids', [])
    #
    #         # Initialize a counter variable to assign a unique index for each product
    #         # Assuming wz.check_ids.ids is a list of IDs and wz.current_check_id.id is the ID to find
    #
    #
    #         index_counter = 0
    #
    #         # Iterate through the products and corresponding check_ids
    #         for product, check_id in zip(self, check_ids):
    #             # Update the context with the current product's check_id and index
    #             new_context['context'].update({
    #                 'default_check_ids': [index_counter],
    #                 'default_current_check_id': index_counter,
    #             })
    #
    #             # Increment the counter for the next product
    #             index_counter += 1
    #
    #         print('22222', new_context)
    #
    #         # Return the modified context
    #         return new_context

    # def check_quality(self):
    #     print('Original context:', self.env.context)
    #     picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
    #     print(self.ids)
    #
    #     # Process each product separately
    #     for product_id in self.ids:
    #         if picking_id:
    #             # Retrieve the relevant check_id for the current product
    #             check_id = self._get_check_id_for_product(product_id, picking_id.check_ids)  # Pass available check_ids
    #
    #             if check_id:
    #                 # Set the context for the current check_id and product_id
    #                 context = {
    #                     'stock_picking': picking_id.id,
    #                     'default_check_id': check_id.id,
    #                     'default_current_check_id': check_id.id,
    #                 }
    #
    #                 # Call the check_quality method on the picking_id with the updated context
    #                 new_context = picking_id.with_context(context).check_quality()
    #
    #                 # Optionally remove 'form_view_ref' if it exists
    #                 if 'form_view_ref' in new_context['context']:
    #                     del new_context['context']['form_view_ref']
    #
    #                 # Open the wizard directly using the appropriate method (replace if needed)
    #                 action = self.browse(product_id).action_open_quality_check_wizard()
    #                 return action  # Return the action immediately for each product
    #
    #     # If no valid picking_id or product_ids are found, return a dummy context
    #     return {'context': {}}

#workingggg
# class StockPickingClass(models.Model):
#     _inherit = 'stock.picking'
#
#     def check_quality_for_product(self, product=None):
#         self.ensure_one()
#         print('self', self)
#
#         if product:
#             checkable_products = self.mapped('move_line_ids').filtered(
#                 lambda line: line.product_id == product).mapped('product_id')
#         else:
#             checkable_products = self.mapped('move_line_ids').mapped('product_id')
#
#         print('checkable_products', checkable_products)
#         checks = self.check_ids.filtered(lambda check: check.quality_state == 'none' and (
#                     check.product_id in checkable_products or check.measure_on == 'operation'))
#         print('checks', checks)
#
#         if checks:
#             print('tttttttttttttttttttt', checks.action_open_quality_check_wizard())
#             return checks.action_open_quality_check_wizard()
#
#         return False
#
# class StockMoveClass(models.Model):
#     _inherit = 'stock.move'
#     quality_check_todo = fields.Boolean('Pending checks', compute='_compute_check', invisible=True)
#     quality_check_fail = fields.Boolean(compute='_compute_check')
#
#     def check_quality(self):
#         print('move_line_ids', self.move_line_ids)
#         print('Original context:', self.env.context)
#         picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
#         print(self.ids)
#
#         print('picking_id', picking_id)
#         print('picking_id.state:', picking_id.state)
#
#         if picking_id:
#             for move_line in self.move_line_ids:
#                 new_context = picking_id.check_quality_for_product(move_line.product_id)
#
#                 if new_context:
#                     new_context['context'].update({
#                         'stock_picking': picking_id.id
#                     })
#
#                     print('1111', new_context)
#                     del new_context['context']['form_view_ref']
#                     print('22222', new_context)
#
#                     # Return the modified context
#                     return new_context
#
#         return False
#
#     @api.depends('picking_id.check_ids', 'picking_id.check_ids.quality_state')
#     def _compute_check(self):
#         for move in self:
#             todo = False
#             fail = False
#             picking = move.picking_id
#             checkable_products = picking.mapped('move_line_ids').mapped('product_id')
#             for check in picking.check_ids:
#                 if check.quality_state == 'none' and (
#                         check.product_id in checkable_products or check.measure_on == 'operation'):
#                     todo = True
#                 elif check.quality_state == 'fail':
#                     fail = True
#                 if fail and todo:
#                     break
#             move.quality_check_fail = fail
#             move.quality_check_todo = todo



        # print('move_line_ids', self.move_line_ids)
        # print('Original context:', self.env.context)
        # picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
        # print(self.ids)
        #
        # actions = []  # Initialize an empty list to store the actions
        #
        # if picking_id:
        #     # Call the check_quality method on the picking_id
        #     new_context = picking_id.check_quality()
        #
        #     new_context['context'].update({
        #         'stock_picking': picking_id.id
        #     })
        #
        #     print('1111', new_context)
        #
        #     # Iterate through move_line_ids
        #     for move_line_id in self.move_line_ids:
        #         # Update the context with the current move_line_id
        #         new_context['context'].update({
        #             'default_check_ids': [move_line_id.id],
        #             'default_current_check_id': move_line_id.id,
        #         })
        #
        #         # Append the context to the list of actions
        #         actions.append(new_context.copy())  # Use copy to avoid modifying the same dictionary instance
        #
        #     del new_context['context']['form_view_ref']
        #     print('22222', new_context)
        #
        # return actions  # Return the list of actions



class QualityInheritNew(models.TransientModel):
    _inherit = 'quality.check.wizard'
    stock_picking=fields.Many2one('stock.picking')



# class ProductTemplateInherit(models.Model):
#     _inherit = 'product.template'
#
#     @api.model
#     def update_product_categories(self):
#         print("AAAAAAAA")
#         today = datetime.now().date()
#         # today = '07/22/2024 10:53:41'
#         products_to_update = self.env['product.template'].search([('expiry_date', '=', today)])
#         print(self.expiry_date)
#
#         # active_category_id = 10  # Replace with the actual ID of the "Active" category
#         # excipient_category_id = 11  # Replace with the actual ID of the "Excipient" category
#         active_name='Active'
#         excipient_name='Exipient'
#
#         # products_to_update.write({'id': excipient_category_id})
#         products_to_update.write({'name': excipient_name})


# workinggg
# class ProductTemplateInherit(models.Model):
#     _inherit = 'product.template'
#
#     @api.model
#     def update_product_categories(self):
#         today = datetime.now().date()
#         print("Today:", today)
#         # products_to_update = self.env['product.template'].search([('expiry_date', '=', today)])
#         products_to_update = self.env['product.template'].search(
#             [('expiry_date', '>=', today), ('expiry_date', '<', today + timedelta(days=1))])
#
#         print(self.expiry_date)
#         print("AAA")
#
#         active_name = 'Active'
#         excipient_name = 'Exipient'
#
#         active_category = self.env['product.category'].search([('name', '=', active_name)], limit=1)
#         excipient_category = self.env['product.category'].search([('name', '=', excipient_name)], limit=1)
#         # print(self.active_category,self.excipient_category)
#
#         if active_category and excipient_category:
#             active_category_id = active_category.id
#             excipient_category_id = excipient_category.id
#
#             products_to_update.write({'categ_id': excipient_category_id})


# class ProductTemplateInherit(models.Model):
#     _inherit = 'product.template'
#
#     @api.model
#     def update_product_categories(self):
#         today = datetime.now().date()
#         products_to_update = self.env['product.template'].search([('expiry_date', '>=', today), ('expiry_date', '<', today + timedelta(days=1))])
#
#         active_name = 'Active'
#         excipient_name = 'Exipient'
#         reanalysis_location_name = 'Reanalysis'
#
#         active_category = self.env['product.category'].search([('name', '=', active_name)], limit=1)
#         excipient_category = self.env['product.category'].search([('name', '=', excipient_name)], limit=1)
#         reanalysis_location = self.env['stock.location'].search([('name', '=', reanalysis_location_name)], limit=1)
#
#         if active_category and excipient_category and reanalysis_location:
#             active_category_id = active_category.id
#             excipient_category_id = excipient_category.id
#             reanalysis_location_id = reanalysis_location.id
#
#             # Update product categories
#             products_to_update.write({'categ_id': excipient_category_id})
#
#             # Move products to the Reanalysis location
#             for product in products_to_update:
#                 move_vals = {
#                     'name': 'Reanalysis Move',
#                     'product_id': product.product_variant_id.id,
#                     'product_uom_qty': product.qty_available,
#                     'product_uom': product.uom_id.id,
#                     'location_id': product.property_stock_inventory.id,
#                     'location_dest_id': reanalysis_location_id,
#                 }
#                 move = self.env['stock.move'].create(move_vals)
#                 move._action_confirm()
#                 move._action_assign()
#                 move._action_done()


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    @api.model
    def update_product_categories(self):
        today = datetime.now().date()
        print("Today:", today)

        products_to_update = self.env['product.template'].search(
            [('expiry_date', '>=', today), ('expiry_date', '<', today + timedelta(days=1))])

        active_name = 'Active'
        excipient_name = 'Excipient'
        reanalysis_location_name = 'Reanalysis'

        active_category = self.env['product.category'].search([('name', '=', active_name)], limit=1)
        excipient_category = self.env['product.category'].search([('name', '=', excipient_name)], limit=1)
        reanalysis_location = self.env['stock.location'].search([('name', '=', reanalysis_location_name)], limit=1)
        print(active_category.name, active_category)
        print(excipient_category.name, excipient_category)
        print(reanalysis_location.name, reanalysis_location)

        if active_category and excipient_category and reanalysis_location:
            active_category_id = active_category.id
            excipient_category_id = excipient_category.id

            # Update the category to Excipient
            products_to_update.write({'categ_id': excipient_category_id})

            reanalysis_location = self.env['stock.location'].search([('name', '=', 'Reanalysis')])
            location_id = reanalysis_location.id


            # if products_to_update.categ_id.id == excipient_category_id:
                # Option 1: Search for product and create stock.quant (if needed)
                # product_record = self.env['product.product'].search(
                #     [('name', '=', 'A')])  # Adjust search criteria as needed
            stock_location = self.env['stock.location'].search([('name', '=', 'Stock')])

            # Dynamically search for the product in the "Stock" location
            product_records = self.env['product.product'].search([
                ('location_id', '=', stock_location.id),
                ('categ_id.name', '=', 'Active')
            ])
            picking =self.env['stock.picking'].with_context(default_picking_type_id=self.env.ref('stock.picking_type_out'))
            if product_records:
                for product_record in product_records:
                    self.env['stock.quant'].create({

                        'product_id': product_record.id,

                        'location_id': location_id,

                })

            if product_records:
                for product_record in product_records:
                    self.env['stock.move.line'].create({
                        'move_id': picking.move_ids_without_package.id,
                        'product_id': product_record.id,
                        'quantity': 1.0,
                        'company_id':1,
                        'location_id': location_id,
                        'location_dest_id':location_id,
                        'state':'done'
                })
                print("Done", product_records.name)


            # Change product location to Reanalysis
            reanalysis_location = self.env['stock.location'].search([('name', '=', 'Reanalysis')])
            # products_to_update.write({'location_id': reanalysis_location.id})

            print(products_to_update.location_id.name, products_to_update.location_id)

##code to put the quality check button in stock.move tree view in purchase order
class StockPickingClass(models.Model):
    _inherit = 'stock.picking'

    def check_quality_for_product(self, product=None):
        self.ensure_one()
        print('self', self)

        if product:
            checkable_products = self.mapped('move_line_ids').filtered(
                lambda line: line.product_id == product).mapped('product_id')
        else:
            checkable_products = self.mapped('move_line_ids').mapped('product_id')

        print('checkable_products', checkable_products)
        checks = self.check_ids.filtered(lambda check: check.quality_state == 'none' and (
                    check.product_id in checkable_products or check.measure_on == 'operation'))
        print('checks', checks)

        if checks:
            print('tttttttttttttttttttt', checks.action_open_quality_check_wizard())
            return checks.action_open_quality_check_wizard()
        if not checks:
            print("Error bro",self.product_id.name)
            raise ValidationError(_("No quality checks found for the selected product(s): %s") % product.display_name)

        return False

class StockMoveClass(models.Model):
    _inherit = 'stock.move'
    quality_check_todo = fields.Boolean('Pending checks', compute='_compute_check', invisible=True)
    quality_check_fail = fields.Boolean(compute='_compute_check')


    def check_quality(self):
        print('move_line_ids', self.move_line_ids)
        print('Original context:', self.env.context)
        picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])
        print(self.ids)

        print('picking_id', picking_id)
        print('picking_id.state:', picking_id.state)

        if picking_id:

            for move_line in self.move_line_ids:

                    new_context = picking_id.check_quality_for_product(move_line.product_id)


                    if new_context:
                        new_context['context'].update({
                            'stock_picking': picking_id.id
                        })
                        

                        print('1111', new_context)
                        del new_context['context']['form_view_ref']
                        print('22222', new_context)

                        # Return the modified context
                        return new_context
            return False

    @api.depends('picking_id.check_ids', 'picking_id.check_ids.quality_state')
    def _compute_check(self):
        for move in self:
            todo = False
            fail = False
            picking = move.picking_id
            checkable_products = picking.mapped('move_line_ids').mapped('product_id')
            for check in picking.check_ids:
                if check.quality_state == 'none' and (
                        check.product_id in checkable_products or check.measure_on == 'operation'):
                    todo = True
                elif check.quality_state == 'fail':
                    fail = True
                if fail and todo:
                    break
            move.quality_check_fail = fail
            move.quality_check_todo = todo

class TestMove(models.Model):
    _inherit="stock.move.line"

    quality_check_done = fields.Boolean(default=False)


# class QualityCheckLocation(models.Model):
#     _inherit = 'quality.check'
#
#     stock_picking = fields.Many2one('stock.picking')
#
#     def do_pass(self):
#         active_id = self._context.get('stock_picking')
#         print('active_id',active_id)
#         # active_id = self._context.get('params').get('id',False)
#         stock_picking_id = self.env['stock.picking'].browse(active_id)
#         print(active_id, 'aaaaaaaaaaaaa')
#         self.stock_picking = stock_picking_id.id
#         if self.stock_picking.id:
#             res = super(QualityCheckLocation, self).do_pass()
#             print('resssssssssssssssssssssssssssssssssssssss', res)
#             stock_picking_id.location_dest_id = self.env['stock.location'].search([('is_unrestricted', '=', True)]).id
#             pass
#         else:
#             raise ValidationError('Please refresh page and try again')
#
#     def do_fail(self):
#         active_id = self._context.get('stock_picking')
#         print(active_id)
#         # active_id = self._context.get('params').get('id',False)
#         stock_picking_id = self.env['stock.picking'].browse(active_id)
#         # print(active_id, 'aaaaaaaaaaaaa')
#         self.stock_picking = stock_picking_id.id
#         if self.stock_picking.id:
#             res = super(QualityCheckLocation, self).do_fail()
#             print('resssssssssssssssssssssssssssssssssssssss', res)
#             stock_picking_id.location_dest_id = self.env['stock.location'].search([('is_restricted', '=', True)]).id
#             pass
#         else:
#             raise ValidationError('Please refresh page and try again')


# class CheckQualityInheritNew(models.Model):
#     _inherit = 'stock.picking'
#
#     def check_quality(self):
#         x = super(CheckQualityInheritNew, self).check_quality()
#
#         if isinstance(x, dict) and 'context' in x:
#
#             x['context'].update({
#                 'stock_picking': self.id
#             })
#
#             print(x)
#             return x

# #
# # class StockingLocationNewTest(models.Model):
# #     _inherit = "stock.location"
# #
# #     is_restricted = fields.Boolean(string='Is restricted')
# #     is_unrestricted = fields.Boolean(string='Is Unrestricted')


# class CustomQualityCheckLocation(models.Model):
#     _inherit = 'quality.check'
#
#     stock_picking = fields.Many2one('stock.picking')
#     # stock_picking = fields.Many2one('stock.picking')
#     test_id=fields.Many2one('quality.check')
#
#     #
#     #     def do_pass(self):
#     #         active_id = self._context.get('stock_picking')
#     #         print('active_id',active_id)
#     #         # active_id = self._context.get('params').get('id',False)
#     #         stock_picking_id = self.env['stock.picking'].browse(active_id)
#
#     def do_pass(self):
#         active_id = self._context.get('test_id')
#         print(active_id)
#         # Move to unrestricted location
#         if self.picking_id:
#             super(CustomQualityCheckLocation, self).do_pass()
#             self.stock_picking.move_to_unrestricted_location()
#
#     def do_fail(self):
#         super(CustomQualityCheckLocation, self).do_fail()
#         # Move to restricted location
#         if self.stock_picking:
#
#             self.stock_picking.move_to_restricted_location()
#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     def move_to_unrestricted_location(self):
#         # Code to move the picking to unrestricted location
#         # Example: Set the destination location to unrestricted
#         self.location_dest_id = self.env['stock.location'].search([('name', '=', 'Unrestricted')], limit=1)
#         print('location_dest_id',self.location_dest_id)
#
#     def move_to_restricted_location(self):
#         # Code to move the picking to restricted location
#         # Example: Set the destination location to restricted
#         self.location_dest_id = self.env['stock.location'].search([('name', '=', 'Restricted')], limit=1)
#         print('location_dest_id', self.location_dest_id)



# class CustomQualityCheckLocation(models.Model):
#     _inherit = 'quality.check'
#
#     # Add a field to store the product's current location
#     current_location_id = fields.Many2one('stock.location', string='Current Location')
#
#     # Add fields to specify unrestricted and restricted locations
#     unrestricted_location_id = fields.Many2one('stock.location', string='Unrestricted Location', required=True)
#     restricted_location_id = fields.Many2one('stock.location', string='Restricted Location', required=True)
#
#     @api.model
#     def _move_product(self, product_id, destination_location_id):
#         """
#         Moves the product to the specified destination location.
#
#         Args:
#             product_id (int): ID of the product to move.
#             destination_location_id (int): ID of the destination location.
#         """
#         try:
#             # Use move.create instead of write for better handling
#             move = self.env['stock.move'].create({
#                 'product_id': product_id,
#                 'product_uom_qty': 1,  # Adjust quantity as needed
#                 'product_uom': self.env['product.uom'].search([('category_id', '=', self.env.ref('uom.product_uom_category_unit').id)], limit=1),
#                 'location_id': self.current_location_id.id,
#                 'location_dest_id': destination_location_id,
#             })
#             move._action_confirm()
#             move._action_assign()
#             move.move_line_ids.write({'qty_done': 1})  # Mark as done
#             move._action_done()
#             _logger.info(f"Successfully moved product {product_id} to {destination_location_id}")
#         except Exception as e:
#             _logger.error(f"Failed to move product {product_id}: {e}")
#
#     def do_pass(self):
#         """
#         Handles the "pass" button click.
#
#         Moves the product to the unrestricted location and updates its quality state.
#         """
#         for record in self:
#             # Fetch the product ID from the existing quality check
#             product_id = record.product_id.id  # Assuming a product_id field in the quality check model
#
#             # Move the product to the unrestricted location
#             record._move_product(product_id, record.unrestricted_location_id.id)
#
#             # Update the quality state
#             record.write({'quality_state': 'pass', 'control_date': datetime.now()})
#
#     def do_fail(self):
#         """
#         Handles the "fail" button click.
#
#         Moves the product to the restricted location and updates its quality state.
#         """
#         for record in self:
#             # Fetch the product ID from the existing quality check
#             product_id = record.product_id.id
#
#             # Move the product to the restricted location
#             record._move_product(product_id, record.restricted_location_id.id)
#
#             # Update the quality state
#             record.write({'quality_state': 'fail', 'control_date': datetime.now()})

# from odoo import models, api
#
# class CustomQualityCheckLocation(models.Model):
#     _inherit = 'quality.check'
#
#     def do_pass(self):
#         picking_id = self.picking_id
#         if picking_id:
#             print(picking_id)
#             res = super(CustomQualityCheckLocation, self).do_pass()
#             print('resss',res)
#             # if res is None:
#             #     res = True  # Assuming success if res is None
#             picking_id.location_dest_id = self.env['stock.location'].search([('name', '=', 'Unrestricted')]).id
#             return res
#         else:
#             raise ValidationError('Please refresh page and try again')
#
#     def do_fail(self):
#         res = super(CustomQualityCheckLocation, self).do_fail()
#         # Move the product to the Restricted location
#         self.env['stock.location'].search([
#             ('name', '=', 'Restricted'),
#         ]).write({'location_dest_id': self.env.ref('purchase_changes.restricted_location_id').id})
#         return res
#

# import logging
# from odoo import models, fields, a

# _logger = logging.getLogger(__name__)
#
# class CustomQualityCheckLocation(models.Model):
#     _inherit = 'quality.check'
#
#     picking_id = fields.Many2one('stock.picking', string='Picking')
#
#     def do_pass(self):
#         """
#         Handles the "pass" button click or action trigger.
#
#         - Calls the original `do_pass` method to ensure its functionality.
#         - Moves the product to the unrestricted location if `picking_id` exists.
#         - Handles potential errors and provides informative messages.
#         """
#         for record in self:
#             try:
#                 picking_id = record.picking_id
#                 id=record.id
#
#                 _logger.debug(f"do_pass for quality check {record.id} with picking {picking_id.id}")
#
#
#                 # Call original do_pass first:
#                 res = super(CustomQualityCheckLocation, record).do_pass()
#
#                 if picking_id:
#                     try:
#                         unrestricted_location = self.env['stock.location'].search([('is_unrestricted', '=', True)], limit=1)
#                         print(unrestricted_location.name)
#                         print('id',id)
#                         if unrestricted_location:
#                             # Move the product using a more efficient method if possible:
#                             picking_id.location_dest_id = self.env['stock.location'].search(
#                                 [('is_unrestricted', '=', True)]).id
#                             print('picking_id.location_dest_id',picking_id.location_dest_id)
#                             pass
#                             picking_id.write({'location_dest_id': unrestricted_location.id})
#                             _logger.info(f"Moved product in picking {picking_id.id} to unrestricted location {unrestricted_location.name}")
#                         else:
#                             _logger.warning("Unrestricted location not found")
#                     except Exception as e:
#                         _logger.error(f"Failed to move product in picking {picking_id.id}: {e}")
#                         raise ValidationError("Failed to move product to unrestricted location: %s" % str(e))
#
#                 return res
#             except Exception as e:
#                 _logger.error(f"Error in do_pass: {e}")
#                 raise ValidationError("An error occurred: %s" % str(e))
#
#     def do_fail(self):
#         """
#         Handles the "fail" button click or action trigger.
#
#         - Calls the original `do_fail` method to ensure its functionality.
#         - Moves the product to the restricted location.
#         - Handles potential errors and provides informative messages.
#        # from odoo import models, api
# #
# # class CustomQualityCheckLocation(models.Model):
# #     _inherit = 'quality.check'
# #
# #     def do_pass(self):
# #         picking_id = self.picking_id
# #         if picking_id:
# #             print(picking_id)
# #             res = super(CustomQualityCheckLocation, self).do_pass()
# #             print('resss',res)
# #             # if res is None:
# #             #     res = True  # Assuming success if res is None
# #             picking_id.location_dest_id = self.env['stock.location'].search([('name', '=', 'Unrestricted')]).id
# #             return res
# #         else:
# #             raise ValidationError('Please refresh page and try again')
# #
# #     def do_fail(self):
# #         res = super(CustomQualityCheckLocation, self).do_fail()
# #         # Move the product to the Restricted location
# #         self.env['stock.location'].search([
# #             ('name', '=', 'Restricted'),
# #         ]).write({'location_dest_id': self.env.ref('purchase_changes.restricted_location_id').id})
# #         return res
# #
#  """
#         for record in self:
#             try:
#                 _logger.debug(f"do_fail for quality check {record.id}")
#
#                 # Call original do_fail first:
#                 res = super(CustomQualityCheckLocation, record).do_fail()
#
#                 try:
#                     restricted_location = self.env['stock.location'].search([('name', '=', 'Restricted')], limit=1)  # Assuming defined by reference
#                     if restricted_location:
#                         # Move the product using a more efficient method if possible:
#                         self.env['stock.location'].search([('id', '=', restricted_location.id)]).write({'location_id': restricted_location.id})
#                         _logger.info(f"Moved product in quality check {record.id} to restricted location {restricted_location.name}")
#                     else:
#                         _logger.warning("Restricted location not found")
#                 except Exception as e:
#                     _logger.error(f"Failed to move product in quality check {record.id}: {e}")
#                     raise ValidationError("Failed to move product to restricted location: %s" % str(e))
#
#                 return res
#             except Exception as e:
#                 _logger.error(f"Error in do_fail: {e}")
#                 raise ValidationError("An error occurred: %s" % str(e))
#


# workinggg
# class CustomQualityCheckLocation(models.Model):
#     _inherit = 'quality.check'
#
#     picking_id = fields.Many2one('stock.picking', string='Picking')
#
    # def do_pass(self):
    #     for rec in self:
    #         picking_id = rec.picking_id
    #         if picking_id:
    #             if picking_id.state != 'done':
    #                 # Validate the picking if it's not already done
    #                 picking_id.button_validate()
    #
    #             # Find the related stock move
    #             stock_move = self.env['stock.move'].search([
    #                 ('picking_id', '=', picking_id.id),
    #                 ('product_id', '=', rec.product_id.id),
    #                 ('state', '=', 'assigned')  # Consider only assigned moves
    #             ], limit=1)
    #
    #             if stock_move:
    #                 # Update the destination location of the stock move
    #                 unrestricted_location = self.env['stock.location'].search([('is_unrestricted', '=', True)], limit=1)
    #                 if unrestricted_location:
    #                     # Update the destination location of the stock move
    #                     stock_move.write({'location_dest_id': unrestricted_location.id})
    #
    #                     # Update the state of related stock move lines to 'done'
    #                     stock_move.move_line_ids.write({'state': 'done'})
    #
    #                     # Call the original do_pass method
    #                     return super(CustomQualityCheckLocation, rec).do_pass()
    #                 else:
    #                     raise ValidationError('Unrestricted location not found')
    #             else:
    #                 raise ValidationError('No stock move found for quality check')
    #         else:
    #             raise ValidationError('Please refresh page and try again')
#
#     def do_fail(self):
#         for rec in self:
#             picking_id = rec.picking_id
#             if picking_id:
#                 # Find the related stock move
#                 stock_move = self.env['stock.move'].search([
#                     ('picking_id', '=', picking_id.id),
#                     ('product_id', '=', rec.product_id.id),
#                     ('state', '=', 'assigned')  # Consider only assigned moves
#                 ], limit=1)
#
#                 if stock_move:
#                     # Update the destination location of the stock move
#                     restricted_location = self.env['stock.location'].search([('is_restricted', '=', True)], limit=1)
#                     print(restricted_location.name)
#                     if restricted_location:
#                         # Update the destination location of the stock move
#                         stock_move.write({'location_dest_id': restricted_location.id})
#
#                         # Update the state of related stock move lines to 'done'
#                         stock_move.move_line_ids.write({'state': 'done'})
#
#                         # Call the original do_pass method
#                         return super(CustomQualityCheckLocation, rec).do_fail()
#                     else:
#                         raise ValidationError('Restricted location not found')
#                 else:
#                     raise ValidationError('No stock move found for quality check')
#             else:
#                 raise ValidationError('Please refresh page and try again')

from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import ValidationError

#working along with validate button but for individual products
# class CustomQualityCheckLocation(models.Model):
#
#     _inherit = 'quality.check'
#     picking_id=fields.Many2one('stock.picking')
#
#     def do_pass(self):
#         for rec in self:
#             picking_id = rec.picking_id
#
#             picking_id.button_validate()
#
#             # Find the related stock move
#             stock_move = self.env['stock.move'].search([
#                 ('picking_id', '=', picking_id.id),
#                 ('product_id', '=', rec.product_id.id),
#                 ('state', '=', 'assigned')  # Consider only assigned moves
#             ], limit=1)
#
#             if stock_move:
#                 # Update the destination location of the stock move
#                 unrestricted_location = self.env['stock.location'].search([('is_unrestricted', '=', True)], limit=1)
#                 if unrestricted_location:
#                     # Update the destination location of the stock move
#                     stock_move.write({'location_dest_id': unrestricted_location.id})
#
#                     # Update the state of related stock move lines to 'done'
#                     stock_move.move_line_ids.write({'state': 'done'})
#
#                     # Call the original do_pass method
#                     return super(CustomQualityCheckLocation, rec).do_pass()
#                 else:
#                     raise ValidationError('Unrestricted location not found')
#             else:
#                 raise ValidationError('No stock move found for quality check')
#         else:
#             raise ValidationError('Please refresh page and try again')
#
#     def do_fail(self):
#         for rec in self:
#             picking_id = rec.picking_id
#             if picking_id:
#                 if picking_id.state != 'done':
#                     # Validate the picking if it's not already done
#                     picking_id.button_validate()
#
#                 # Find the related stock move
#                 stock_move = self.env['stock.move'].search([
#                     ('picking_id', '=', picking_id.id),
#                     ('product_id', '=', rec.product_id.id),
#                     ('state', '=', 'assigned')  # Consider only assigned moves
#                 ], limit=1)
#
#                 if stock_move:
#                     # Update the destination location of the stock move
#                     restricted_location = self.env['stock.location'].search([('is_restricted', '=', True)], limit=1)
#                     if restricted_location:
#                         # Update the destination location of the stock move
#                         stock_move.write({'location_dest_id': restricted_location.id})
#
#                         # Call the original do_fail method
#                         return super(CustomQualityCheckLocation, rec).do_fail()
#                     else:
#                         raise ValidationError('Restricted location not found')
#                 else:
#                     raise ValidationError('No stock move found for quality check')
#             else:
#                 raise ValidationError('Please refresh page and try again')
#
#     def button_validate(self):
#         for rec in self:
#
#             rec.picking_id.button_validate()

class CustomQualityCheckLocation(models.Model):
    _inherit = 'quality.check'

    move_lines_ids=fields.Many2one('stock.picking')


    def do_pass(self):
        for rec in self:
            picking_id = rec.picking_id
            if picking_id:
                if picking_id.state != 'done':
                    picking_id.button_validate()
                stock_move = self.env['stock.move'].search([
                    ('picking_id', '=', picking_id.id),
                    ('product_id', '=', rec.product_id.id),
                    ('state', '=', 'assigned')
                ], limit=1)
                if stock_move:
                    unrestricted_location = self.env['stock.location'].search([('name', '=', 'Reanalysis')], limit=1)
                    if unrestricted_location:
                        stock_move.write({'location_dest_id': unrestricted_location.id})
                        stock_move.move_line_ids.write({'state': 'done'})
                        return super(CustomQualityCheckLocation, rec).do_pass()
                    else:
                        raise ValidationError('Reanalysis location not found')
                else:
                    raise ValidationError('No stock move found for quality check')
            else:
                raise ValidationError('Please refresh page and try again')

    def do_fail(self):
        for rec in self:
            picking_id = rec.picking_id

            if picking_id:
                if picking_id.state != 'done':
                    picking_id.button_validate()
                stock_move = self.env['stock.move'].search([
                    ('picking_id', '=', picking_id.id),
                    ('product_id', '=', rec.product_id.id),
                    ('state', '=', 'assigned')
                ], limit=1)

                if stock_move:
                    restricted_location = self.env['stock.location'].search([('name', '=', 'Blocked')], limit=1)
                    if restricted_location:
                        stock_move.write({'location_dest_id': restricted_location.id})
                        return super(CustomQualityCheckLocation, rec).do_fail()
                    else:
                        raise ValidationError('Blocked location not found')
                else:
                    raise ValidationError('No stock move found for quality check')
            else:
                raise ValidationError('Please refresh page and try again')

    def button_validate(self):
        for rec in self:
            print(rec.picking_id)
            rec.picking_id.button_validate()
