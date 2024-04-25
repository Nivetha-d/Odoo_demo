# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
from odoo.exceptions import ValidationError
from datetime import datetime


class purchaserequesition(models.Model):
    _name = 'purchase.newchanges'
    _inherit = ['portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin']

    # requition_action = fields.Char(string='Requition Action')

    is_verified = fields.Boolean("verify")
    is_req_sent = fields.Boolean("send")

    # emp_name = fields.Many2one('hr.employee', string='Employee Name')
    em_name=fields.Many2one('res.users',string="Employee Name",required=True)
    department_name = fields.Many2one('hr.department', string='Department Name')
    managers_id = fields.Many2one('hr.department', string='Department Manager')
    req_date = fields.Date('Request Date')
    src_location = fields.Many2one('stock.quant', string='Source Location')
    destination_location = fields.Many2one('stock.quant', string='Destination Location')
    deliver_to = fields.Many2one('stock.picking.type', string='Deliver To')
    internal_picking = fields.Many2one('stock.picking.type', string='Internal Picking Location')

    name = fields.Char('Order Reference', required=True, index='trigram', copy=False, default='New')
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    purchase_count = fields.Integer(compute="_compute_purchase_count")
    invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills', copy=False, store=True)
    prod_line_ids = fields.One2many('pur.req.lines', 'pur_id', string='Products')
    requisition_action = fields.Many2one('stock.picking.type', string='Requisition Action')
    vendor_name = fields.Many2one('res.partner', string='Vendor Name',
                                  domain=[('is_company', '=', True),
                                          ('invoice_ids.name', '!=',
                                           False)])
    p_unit_price=fields.Many2one('pur.req.lines',string="Price")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        # ('department', 'Department Approved'),
        ('department', 'Department Approval'),
        ('approve', 'Approved'),
        ('po created', 'PO Created'),
        ('cancel', 'Cancelled')

    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    @api.depends('prod_line_ids')
    def _compute_purchase_count(self):
        for record in self:
            product_ids = record.prod_line_ids.mapped('product_id')
            purchase_orders = self.env['purchase.order'].search([('product_id', 'in', product_ids.ids)])
            record.purchase_count = len(purchase_orders)

    def action_my_smart_button(self):
        if self.purchase_count > 0:
            purchase_order = self.env['purchase.order'].search([('product_id', '=', self.prod_line_ids.product_id.id)],
                                                               limit=1)
            if purchase_order:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Purchase Order',
                    'res_model': 'purchase.order',
                    'view_mode': 'tree,form',
                    'domain': [('product_id', '=', self.prod_line_ids.product_id.id)],
                }
        return {}

    # @api.depends('invoice_count')
    # def _compute_purchase_order(self):
    #     purchase_order = self.env['purchase.order'].search([('pur_req', '=', self.id)])
    #     print(purchase_order)
    #     self.invoice_count = len(purchase_order)
    #

    # # @api.depends('order_line.invoice_lines.move_id')
    # def _compute_invoice(self):
    #     for order in self:
    #         pass
    #         invoices = order.mapped('order_line.invoice_lines.move_id')
    #         order.invoice_ids = invoices
    #         order.invoice_count = len(invoices)

    def action_view_invoice(self):
        pass

    def button_confirm_new(self):
        for rec in self:
            self.state = 'confirm'

    def req_send_department(self):
        for rec in self:
            self.state = 'department'

    def approve_quotation(self):
        for rec in self:
            self.state = 'approve'
        # if (self.is_verified == True):
        #     return super(purchaserequesition, self).button_confirm_new()
        # else:
        #     raise ValidationError("Request not Approved by Department")

    def reset_to_draft(self):
        for rec in self:
            rec.is_verified = True
            rec.is_req_sent = False
            self.state = 'draft'

    def button_reject(self):
        for rec in self:
            rec.is_verified = True
            rec.is_req_sent = False
            self.state = 'cancel'

    # def purchase_quotation(self):
    #     print("raj")
    #     self.ensure_one()
    #     self.state = 'po created'
    #
    #     # Retrieve the partner_id from the related model or from the current model
    #     partner_id = self.partner_id.id if hasattr(self, 'partner_id') else False
    #
    #     if not partner_id:
    #         # Handle the case where partner_id is not set
    #         # You might want to raise an exception, log a warning, or perform some other action
    #         pass
    #
    #     # Retrieve purchase order lines based on pur.req.lines
    #     order_lines = []
    #     for line in self.prod_line_ids:
    #         # Retrieve the price_unit from pur.req.lines
    #         price_unit = line.requisition_action.price_unit if line.requisition_action else line.price_unit
    #
    #         order_line = (0, 0, {
    #             'product_id': line.product_id.id,
    #             'requisition_action': line.requisition_action.id,
    #             'name': line.name,
    #             'product_qty': line.product_uom_qty,
    #             'price_unit': price_unit,
    #             'date_planned': datetime.now(),
    #             'product_uom': line.uom_id.id,
    #         })
    #         order_lines.append(order_line)
    #
    #     # Set up the action dictionary with the necessary context and res_id
    #     action = {
    #         'name': 'Purchase Order',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.order',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('purchase.purchase_order_form').id,
    #         'view_type': 'form',
    #         'res_0.00id': False,  # Set to False to open a new record
    #         'context': {
    #             'default_partner_id': partner_id,
    #             'default_origin': self.name,
    #             'default_opportunity_id': self.id,
    #             'default_pur_req': self.id,
    #             'default_order_line': order_lines,
    #             'default_vendor_name': self.vendor_name,  # Assuming vendor_name is a field in your model
    #             # Add other default values as needed
    #         },
    #     }
    #
    #     return action





    def purchase_quotation(self):

        self.ensure_one()
        self.state = 'po created'
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]

        line_vals = []
        for rec in self:
            for line in rec.prod_line_ids:
                # price_unit = line.requisition_action.price_unit if line.requisition_action else line.price_unit
                # price_unit =self.env.ref('pur.req.lines').search[('price_unit')]
                lines = {
                    'product_id': line.product_id.id,
                    'requisition_action': line.requisition_action.id,
                    'name': line.name,
                    'product_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'date_planned': datetime.now(),
                    'product_uom': line.uom_id.id,

                }
                print(line.price_unit)
                line_vals.append(Command.create(lines))
                print(line_vals)

                action['context'] = {
                    'default_requisition_action': self.requisition_action.id,
                    'default_order_line': line_vals,
                    'default_origin': self.name,
                    'default_opportunity_id': self.id,
                    'default_pur_req': self.id,
                    'default_partner_id': self.vendor_name
                }

            return action


class purchase_changes(models.Model):
    _inherit = 'purchase.order'

    pur_req = fields.Many2one('purchase.newchanges', string='Pur Req')

    # def write(self, vals):
    #     # print(vals)
    #     # print(vals.get())
    #     return super(purchase_changes, self).write(vals)
    #
    # def create(self, vals):
    #     # print(vals)
    #     # print(vals.get())
    #     return super(purchase_changes, self).create(vals)
    #
    #


class purchase_changes_line(models.Model):
    _inherit = 'purchase.order.line'

    requisition_action = fields.Many2one('stock.picking.type', string='Requisition Action')


class StockingPickingNew(models.Model):
    _inherit = "stock.picking"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Received'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
