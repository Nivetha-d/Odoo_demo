from odoo import fields, api, models
from odoo.exceptions import ValidationError


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
    quantity = fields.Float(string='Quantity')


    @api.onchange('product_id')
    def prod_onchange_get_order_id(self):
        for rec in self:
            self.price_unit = rec.product_id.standard_price
            self.uom_id = rec.product_id.uom_id.id
            self.name = rec.product_id.name


class LocationQuality(models.Model):
    _inherit = 'quality.point'

    src_location = fields.Many2one('stock.location', string='Source Location')
    destination_location = fields.Many2one('stock.location', string='Destination Location')


class QualityCheckWizardNew(models.TransientModel):
    _inherit = 'quality.check.wizard'

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
            # print('resssssssssssssssssssssssssssssssssssssss', res)
            stock_picking_id.location_dest_id = self.env['stock.location'].search([('is_restricted', '=', True)]).id
            pass
        else:
            raise ValidationError('Please refresh page and try again')


class CheckQualityInherit(models.Model):
    _inherit = 'stock.picking'

    def check_quality(self):
        x = super(CheckQualityInherit, self).check_quality()

        x['context'].update({
            'stock_picking': self.id
        })

        print(x)
        return x



class StockingLocationNew(models.Model):
    _inherit = "stock.location"

    is_restricted = fields.Boolean(string='Is restricted')
    is_unrestricted = fields.Boolean(string='Is Unrestricted')
    is_retest = fields.Boolean(string='Is Retest/Reanalysis')
    is_blocked = fields.Boolean(string='Is Blocked')




class CustomStockMove(models.Model):

    _inherit = 'stock.move'


    def check_quality(self):
        print('Original context:', self.env.context)
        picking_id = self.env['stock.picking'].browse(self.env.context['default_picking_id'])

        # picking_id = self.env['stock.picking'].search([('id')])
        print('picking_id', picking_id)

        if picking_id:
            # Call the check_quality method on the picking_id

            new_context = picking_id.check_quality()

            new_context['context'].update({
                'stock_picking': picking_id.id
            })

            print('1111', new_context)
            del new_context['context']['form_view_ref']
            print('22222', new_context)

            # Return the modified context
            return new_context

class QualityInheritNew(models.TransientModel):
    _inherit = 'quality.check.wizard'
    stock_picking=fields.Many2one('stock.picking')