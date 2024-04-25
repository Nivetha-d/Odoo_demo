from odoo import models, api,_,fields
from odoo.tools import format_date

class CustomDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_partner_name(self):
        partner = self.partner_id
        for record in self:
            if record.state in ('draft', 'sent'):
                partner_details = {
                    'name': partner.name or '',
                    'street': partner.street or '',
                    'street2': partner.street2 or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'phone': partner.mobile or '',
                    'email': partner.email or '',
                    'net_amount': self.amount_untaxed or '',
                    'vat_id': partner.vat or '',
                    'tax': self.amount_tax or '',
                    'total': self.amount_tax or '',
                }
                return partner_details
            else:
                partner_details = {
                    'name': partner.name or '',
                    'street': partner.street or '',
                    'street2': partner.street2 or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'phone': partner.mobile or '',
                    'email': partner.email or '',
                    'net_amount': self.amount_untaxed or '',
                    'vat_id': partner.vat or '',
                    'tax': self.amount_tax or '',
                    'total': self.amount_total or '',
                }
                return partner_details

    def get_order_lines(self):

        order_lines = []
        for line in self.order_line:
            line_details = {
                'product': line.product_id.display_name,
                'description':line.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'subtotal': line.price_subtotal,
            }
            order_lines.append(line_details)
        return order_lines

    def _compute_l10n_din5008_template_data(self):
        for record in self:
            record.l10n_din5008_template_data = data = []
            if record.state in ('draft', 'sent'):
                if record.name:
                    data.append((_("Quotation No."), record.name))
                if record.date_order:
                    data.append((_("Quotation Date"), format_date(self.env, record.date_order)))
                if record.user_id:
                    data.append((_("Customer no"), ""))
                # if record:
                #     data.append((_("VAT ID"),record.partner_id.vat))

            else:
                if record.name:
                    data.append((_("Order No."), record.name))
                if record.date_order:
                    data.append((_("Order Date"), record.date_order))
                if record:
                    data.append((_("VAT-ID-No"), record.partner_id.vat))
            if record.client_order_ref:
                data.append((_('Customer Reference'), record.client_order_ref))

            if 'incoterm' in record._fields and record.incoterm:
                data.append((_("Incoterm"), record.incoterm.code))

    # def _compute_l10n_din5008_document_title(self):
    #     return ""

    def _compute_l10n_din5008_document_title(self):
        """Override of l10n_din5008_sale to title pickup receipts."""
        for record in self:
            if (
                    record.state not in ('draft', 'sent')
                    and self._context.get('pickup_receipt')
                    and not self._context.get('proforma')
            ):
                record.l10n_din5008_document_title = _("Pickup Receipt")
            else:
                super(SaleOrder, record)._compute_l10n_din5008_document_title()

    def _compute_l10n_din5008_addresses(self):
        for record in self:
            record.l10n_din5008_addresses = data = []
            if record.state in ('draft', 'sent'):
                data.append((_("Your reference"), ""))
                data.append((_("Your mail to Max"), ""))

                data.append((_(""), format_date(self.env, record.date_order)))

                customer = record.partner_id.name
                data.append((_("Contact person:"),customer))
                data.append((_("E-mail:"),record.partner_id.email))
                data.append((_("Tele-no:"),record.partner_id.mobile))


            else:
                data.append((_("Your order dated:"),record.date_order))
                data.append((_("Order No."), record.name))
                data.append((_("Offer No."), ""))
                customer = record.partner_id.name

                data.append((_("Contact person:"), customer))
                data.append((_("E-mail:"), record.partner_id.email))
                data.append((_("Tele-no:"), record.partner_id.mobile))


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    def get_partner_name(self):
        partner = self.partner_id
        for record in self:
            if record.state in ('draft', 'sent'):
                partner_details = {
                    'name': partner.name or '',
                    'street': partner.street or '',
                    'street2': partner.street2 or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'phone': partner.mobile or '',
                    'email': partner.email or '',
                    'net_amount': self.amount_untaxed or '',
                    'vat_id': partner.vat or '',
                    'tax': self.amount_tax or '',
                    'total': self.amount_total  or '',
                }
                return partner_details
            else:
                partner_details = {
                    'name': partner.name or '',
                    'street': partner.street or '',
                    'street2': partner.street2 or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'phone': partner.mobile or '',
                    'email': partner.email or '',
                     'net_amount': self.amount_untaxed or '',
                    'vat_id': partner.vat or '',
                    'tax': self.amount_tax or '',
                    'total': self.amount_total or '',
                }
                return partner_details

    def _compute_l10n_din5008_template_data(self):
        for record in self:
            record.l10n_din5008_template_data = data = []
            if record.name:
                data.append((_("Invoice No."), record.name))
            if record.invoice_date:
                data.append((_("Invoice Date"), format_date(self.env, record.invoice_date)))
            if record:
                data.append((_("Customer No."), ""))
                data.append((_("Specialist"),""))


    def _compute_l10n_din5008_document_title(self):
        for record in self:
            record.l10n_din5008_document_title = ''
            if record.move_type == 'out_invoice':
                if record.state == 'posted':
                    record.l10n_din5008_document_title = _('Invoice')
                elif record.state == 'draft':
                    record.l10n_din5008_document_title = _('Draft Invoice')
                elif record.state == 'cancel':
                    record.l10n_din5008_document_title = _('Cancelled Invoice')
            elif record.move_type == 'out_refund':
                record.l10n_din5008_document_title = _('Credit Note')
            elif record.move_type == 'in_refund':
                record.l10n_din5008_document_title = _('Vendor Credit Note')
            elif record.move_type == 'in_invoice':
                record.l10n_din5008_document_title = _('Vendor Bill')

    def _compute_l10n_din5008_addresses(self):
        for record in self:
            record.l10n_din5008_addresses = data = []
            # if record.state in ('draft', 'sent'):

            data.append((_("Order No:"), ""))
            data.append((_("Shipping doc,No."), ""))

            data.append((_("Order:"), ""))
            data.append((_("Order Date:"),  format_date(self.env, record.invoice_date)))
            data.append((_("Shipping doc. date:"), format_date(self.env, record.invoice_date)))



    def get_invoice_order_lines(self):
        invoice_lines = []
        for line in self.invoice_line_ids:
            print(line)
            line_details = {
                'product': line.product_id,
                'description': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'subtotal': line.price_subtotal,
            }
            print(line_details['product'].name)
            invoice_lines.append(line_details)
        return invoice_lines

    def check_field_access_rights(self, operation, field_names):
            field_names = super().check_field_access_rights(operation, field_names)
            return [field_name for field_name in field_names if field_name not in {
                'l10n_din5008_addresses',
            }]

class StockPickingReports(models.Model):
    _inherit = 'stock.picking'

    l10n_din5008_template_data = fields.Binary(compute='_compute_l10n_din5008_template_data')
    l10n_din5008_addresses = fields.Binary(compute='_compute_l10n_din5008_addresses', exportable=False)

    def _compute_l10n_din5008_addresses(self):
        for record in self:
            record.l10n_din5008_addresses = data = []
            if record.partner_id:
                if record.picking_type_id.code == 'incoming':
                    data.append((_('Vendor Address:'), record.partner_id))
                if record.picking_type_id.code == 'internal':
                    data.append((_('Warehouse Address:'), record.partner_id))
                if record.picking_type_id.code == 'outgoing' and record.move_ids_without_package and \
                        record.move_ids_without_package[0].partner_id \
                        and record.move_ids_without_package[0].partner_id.id != record.partner_id.id:
                    data.append((_('Customer Address:'), record.partner_id))


    def check_field_access_rights(self, operation, field_names):
        field_names = super().check_field_access_rights(operation, field_names)
        return [field_name for field_name in field_names if field_name not in {
            'l10n_din5008_addresses',
        }]

    def get_partner_name(self):
        partner = self.partner_id
        for record in self:
            if record.state in ('draft', 'sent'):
                partner_details = {
                    'name': partner.name or '',
                    'street': partner.street or '',
                    'street2': partner.street2 or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'phone': partner.mobile or '',
                    'email': partner.email or '',
                    'net_amount': self.amount_untaxed or '',
                    'vat_id': partner.vat or ''
                }
                return partner_details
            else:
                partner_details = {
                    'name': partner.name or '',
                    'street': partner.street or '',
                    'street2': partner.street2 or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'phone': partner.mobile or '',
                    'email': partner.email or '',
                    # 'net_amount': self.amount_untaxed or ''
                }
                return partner_details

    def get_order_lines(self):

        move_details = []
        for move in self.move_ids:
            move_detail = {
                'product': move.product_id.display_name,
                'quantity': move.product_uom_qty,
                'price_unit': move.price_unit,
                'subtotal': move.price_subtotal,
            }
            move_details.append(move_detail)
        return move_details

    def _compute_l10n_din5008_template_data(self):
        for record in self:
            record.l10n_din5008_template_data = data = []
            if record.state in ('draft', 'waiting','confirmed','assigned','done'):
                if record.name:
                    data.append((_("Picking list No."), record.name))
                if record.date_done:
                    data.append((_("Date"), format_date(self.env, record.date_done)))
                if record:
                        data.append((_("Customer no"), ""))
                if record.origin:
                    data.append((_("Order no"),record.origin))

            else:
                if record.name:
                    data.append((_("Order No."), record.name))
                if record.date_done:
                    data.append((_("Order Date"), format_date(self.env, record.date_done)))
               # if record.client_order_ref:
               #  data.append((_('Customer Reference'), record.client_order_ref))

            if 'incoterm' in record._fields and record.incoterm:
                data.append((_("Incoterm"), record.incoterm.code))



    def get_order_details_table(self):

       for record in self:
            order_detail = {
                'Your_order_dated': "",
                'Your_order_of': "",
                'Specialist': "",

            }

            return order_detail


