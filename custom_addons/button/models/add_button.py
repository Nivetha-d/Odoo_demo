# from odoo import models, api, _
# from odoo.exceptions import ValidationError
#
# import mimetypes
# import os
# import logging
# import chardet
# import codecs
#
# _logger = logging.getLogger(__name__)
#
#
# class CustomImport(models.TransientModel):
#     _inherit = 'base_import.import'
#
#
#     def _read_file(self, options):
#         """ Dispatch to specific method to read file content, according to its mimetype or file type
#
#         :param dict options: reading options (quoting, separator, ...)
#         """
#         self.ensure_one()
#
#         FILE_TYPE_DICT = {
#             'text/csv': ('csv', True, None),
#             'application/vnd.ms-excel': ('xls', 'xlrd', 'xlrd'),
#             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', 'xlsx', 'xlrd >= 1.0.0'),
#             'application/vnd.oasis.opendocument.spreadsheet': ('ods', 'odf_ods_reader', 'odfpy'),
#             'text/plain': ('txt', '_read_txt', None)
#         }
#
#         # Guess file type based on file extension
#         file_extension = os.path.splitext(self.file_name or '')[1].lower()
#         handler = FILE_TYPE_DICT.get(file_extension)
#
#         # Add support for TXT files
#         if not handler and file_extension == '.txt':
#             handler = ('txt', '_read_txt', None)
#
#         if handler:
#             try:
#                 return getattr(self, handler[1])(options)
#             except Exception as e:
#                 error_message = "Failed to read file '{}' (transient id {}) with extension {}".format(
#                     self.file_name or '<unknown>', self.id, file_extension)
#                 _logger.warning(error_message)
#                 raise ValidationError(error_message)
#
#             # Continue with existing logic for other file types
#         return super(CustomImport, self)._read_file(options)
#
#
#     def _read_txt(self, options):
#
#         BOM_MAP = {
#             'utf-8': codecs.BOM_UTF8,
#             'utf-16le': codecs.BOM_UTF16_LE,
#             'utf-16be': codecs.BOM_UTF16_BE,
#             'utf-32le': codecs.BOM_UTF32_LE,
#             'utf-32be': codecs.BOM_UTF32_BE,
#         }
#
#
#         txt_data = self.file or b''
#         if not txt_data:
#             return ()
#
#         encoding = options.get('encoding')
#         if not encoding:
#             encoding = options['encoding'] = chardet.detect(txt_data)['encoding'].lower()
#             # Handle BOM for UTF encodings
#             bom = BOM_MAP.get(encoding)
#             if bom and txt_data.startswith(bom):
#                 encoding = options['encoding'] = encoding[:-2]
#
#         try:
#             decoded_text = txt_data.decode(encoding)
#         except UnicodeDecodeError as e:
#             raise ValidationError(_("Error while decoding file: {}").format(str(e)))
#
#         lines = decoded_text.splitlines()
#
#         # Filter out empty lines
#         content = [line.strip() for line in lines if line.strip()]
#         print(content)
#
#         # Return the file length as the first value
#         return len(content), content
#
#
#
# #     partner = fields.Many2one('res.partner',string="Partner")
# #     product_name = fields.Many2one('product.template', string="Product")
# #
# #     @api.onchange('partner')
# #     def onchange_partner(self):
# #         if self.partner:
# #             self.check = True
# #
# #     def action_confirm(self):
# #         if self.partner and self.product_name:
# #             purchase_order = self.env['purchase.order'].create({
# #                 'partner_id': self.partner.id,
# #                 # Add other necessary fields for the purchase order
# #             })
# #
# #             purchase_order_line = self.env['purchase.order.line'].create({
# #                 'order_id': purchase_order.id,
# #                 'product_id': self.product_name.product_variant_id.id,
# #                 'product_qty': 1,  # You may adjust the quantity as needed
# #                 # Add other necessary fields for the purchase order line
# #             })
# #
# #             # You can customize this part based on your specific requirements
# #
# #             return {
# #                 'type': 'ir.actions.act_window',
# #                 'res_model': 'purchase.order',
# #                 'res_id': purchase_order.id,
# #                 'view_mode': 'form',
# #                 'view_id': False,
# #                 'target': 'current',
# #             }
# #         else:
# #             # Handle the case where either partner or product is not selected
# #             return {
# #                 'warning': {
# #                     'title': 'Warning',
# #                     'message': 'Please select both a partner and a product before confirming.',
# #                 }
# #             }
# #
# #
# #
# #
