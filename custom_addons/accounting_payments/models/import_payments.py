from odoo import models, fields,api
import base64
from odoo.exceptions import ValidationError
import os
from decimal import Decimal
from unidecode import unidecode
import werkzeug
from werkzeug.utils import secure_filename
from datetime import datetime

class UploadPayments(models.Model):
    _name = 'upload.payments'

    # Define your wizard fields here
    upload_txt = fields.Binary(string="Payment file upload")
    upload_filename = fields.Char(string="Filename")


    # def submit_button(self):
    #
    #     if not self.upload_txt:
    #         raise ValidationError("Please select a file.")
    #     if not self.upload_filename.lower().endswith('.txt'):
    #         raise ValidationError("Only .txt files are allowed.")
    #
    #     # Decode the binary data and split lines
    #     file_content = base64.decodebytes(self.upload_txt).decode("latin-1")
    #     file_lines = file_content.split("\r\n")
    #
    #
    #     payments = {}
    #
    #     # Extract invoice numbers and amounts from each line
    #     for line in file_lines:
    #         parts = line.split(';')
    #         if len(parts) >= 6:
    #             status_code = parts[0].strip()
    #             print(status_code)
    #             if status_code in ("RA", "RI"):
    #                 # Create a draft vendor bill
    #                 partner_id = self.get_or_create_partner('Adesion').id
    #
    #                 self.create_draft_vendor_bill(parts,partner_id)
    #             invoice_number = parts[3].strip()
    #             a = parts[5]
    #             print(a)
    #             # amount_str = ''.join(c for c in parts[5] if c.isdigit() or c in {',', '.'})
    #             # print(amount_str)
    #             # if '-' in amount_str.split() and any(char.isdigit() for char in amount_str.split('-')[1]):
    #             #     # Skip processing lines with negative amounts
    #             #     continue
    #             amount_str = parts[5].strip()  # Get the amount string
    #
    #             # Skip lines with negative amounts
    #             if '-' in amount_str:
    #                 continue
    #
    #             try:
    #                 amount = float(amount_str.replace(',', ''))
    #
    #                 if amount > 0:  # Only process positive amounts
    #                     if invoice_number in payments:
    #                         payments[invoice_number] += amount  # Sum amounts for the same invoice
    #                     else:
    #                         payments[invoice_number] = amount
    #             except ValueError:
    #                 print("Invalid amount format for line:", line)
    #                 continue
    #
    #     manual_payment_method_line_id = self.env['account.payment.method.line'].search(
    #         [('payment_method_id', '=', 'Manual')],
    #         limit=1)
    #
    #     payment_model = self.env['account.payment']
    #     partner_model = self.env['res.partner']
    #
    #     for invoice_number, amount in payments.items():
    #         payment = payment_model.create({
    #             'ref': invoice_number,
    #             'amount': amount,
    #             'payment_method_line_id': manual_payment_method_line_id.id,
    #         })
    #
    #         if payment.state == 'draft':
    #             for pay in payment.search([('state', '=', 'draft')]):
    #
    #                         pay.write({'payment_method_line_id': manual_payment_method_line_id.id})
    #                         if pay.state == 'draft':
    #                             pay.write({'state': 'posted'})
    #                             invoice = self.env['account.move'].search([('name', '=', invoice_number)], limit=1)
    #                             if invoice:
    #                                 partner_id = invoice.partner_id
    #                                 pay.write({'partner_id': partner_id})
    #
    #                         else:
    #                             raise ValidationError("Payment must be in draft state to be posted")
    #
    #             invoice = self.env['account.move'].search([('name', '=', invoice_number)], limit=1)
    #             if invoice:
    #                 partner_id = invoice.partner_id.id
    #                 payment.write({'partner_id': partner_id})
    #
    #     print("Processed Invoice Numbers and Amounts:")
    #     for invoice_number, amount in payments.items():
    #         print("Invoice Number:", invoice_number, "| Amount:", amount)
    #
    #     # file_name = werkzeug.utils.secure_filename(self.upload_txt.decode('latin-1'))
    #     file_name = self.upload_filename
    #     uploaded_file = self.env['payment.file'].create({
    #         'filename': file_name,
    #         'file_data': self.upload_txt,
    #     })
    #
    #
    #
    #     return uploaded_file

    def get_or_create_partner(self, partner_name):
        partner = self.env['res.partner'].search([('name', '=', partner_name)], limit=1)
        if not partner:
            # Create partner if it doesn't exist
            partner = self.env['res.partner'].create({'name': partner_name})
        return partner

    def create_draft_vendor_bill(self, parts,partner_id):

        vendor_bill = self.env['account.move'].create({
                                                'move_type': 'in_invoice',
            'partner_id': partner_id,
                                           'state': 'draft'
        })
        print("Draft vendor bill created:", vendor_bill)





class YourModule(models.Model):
    _name = 'payment.file'

    filename = fields.Char(string='File')
    date = fields.Date(string="File Date")
    process_pay = fields.Char(string="Process to Payments")
    process_bill = fields.Char(string="Process to Bills")
    file_status_payment = fields.Selection([('processed', 'Processed'),
        ('failed', 'Failed')])
    file_status_bills = fields.Selection([('processed', 'Processed'),
        ('failed', 'Failed')])

    file_data = fields.Binary(string='Abrechnungs-Nr.')


    @api.constrains('file_data')
    def check_duplicate_file(self):
        for record in self:
            if record.filename:
                duplicate_files = self.search([('filename', '=', record.filename), ('id', '!=', record.id)])
                if duplicate_files:
                    raise ValidationError("File with the same name already exists. Please upload a different file.")

    def update_invoice_status(self, invoice,status_code):
        """
        Update the status of invoices based on their associated payments.
        If any payment for an invoice is in draft state or if there are no payments,
        set the invoice status to 'to_upload'. Otherwise, set it to 'factored' or 'admin_started'.
        """
        for invoices in invoice:
            # payment_exists = self.env['account.payment'].search([('ref', '=', invoices.name)])
            # if not payment_exists or any(payment.state == 'draft' for payment in payment_exists):
            #     invoices.write({'status': 'to_upload'})

            if invoices:
                if status_code == 'RA':
                    invoices.write({
                        'status': 'factored',
                    })
                elif status_code == 'RI':
                    invoices.write({
                        'status': 'admin_started',
                    })


    def process_payment(self):

        if not self.file_data:
            raise ValidationError("Please select a file.")
        if not self.filename.lower().endswith('.txt'):
            raise ValidationError("Only .txt files are allowed.")

        file_content = base64.decodebytes(self.file_data).decode("latin-1")

        file_lines = file_content.split("\r\n")


        try:
            payments = {}

            # Extract invoice numbers and amounts from each line
            for line in file_lines:
                parts = line.split(';')
                if len(parts) >= 6:
                    status_code = parts[0].strip()
                    print(status_code)

                    if status_code not in ['RA', 'RI']:
                        continue

                    date_str = parts[6].strip()
                    date_str_cleaned = date_str.strip()  # Remove any leading or trailing spaces

                    try:
                        file_date = datetime.strptime(date_str_cleaned, "%d%m%y").date()
                        self.write({'date': file_date})
                    except ValueError:
                        self.write({'file_status_payment': 'failed'})
                        break



                    invoice_number = parts[3].strip()


                    amount_str = parts[5].strip().replace(' ', '')
                    amount_str = amount_str.replace('.','').replace(',','.')
                    print('AMOUNT:',amount_str)

                    try:

                        amount = float(amount_str)
                        print(amount)
                        # if amount<0:
                        #     self.write({'file_status_payment': 'failed'})
                        #     continue

                        if invoice_number in payments:
                             payments[invoice_number] += amount
                             print(payments[invoice_number])

                        else:
                            payments[invoice_number] = amount
                            print(payments[invoice_number])

                        invoice = self.env['account.move'].search([('name', '=', invoice_number)], limit=1)
                        self.update_invoice_status(invoice,status_code)
                        # if invoice:
                        #     if status_code == 'RA':
                        #         invoice.write({
                        #             'status': 'factored',
                        #         })
                        #     elif status_code == 'RI':
                        #         invoice.write({
                        #             'status': 'admin_started',
                        #         })

                    except ValueError:
                        self.write({'file_status_payment': 'failed'})
                        print("Invalid amount format for line:", line)
                        continue

            # for invoice_number, amount in payments.items():
            #     invoice = self.env['account.move'].search([('name', '=', invoice_number)], limit=1)
            #     if invoice:
            #         payment_exists = self.env['account.payment'].search([('ref', '=', invoice_number)])
            #         if not payment_exists or any(payment.state == 'draft' for payment in payment_exists):
            #             invoice.write({'status': 'to_upload'})


            manual_payment_method_line_id = self.env['account.payment.method.line'].search(
                [('payment_method_id', '=', 'Manual')],
                limit=1)

            payment_model = self.env['account.payment']
            partner_model = self.env['res.partner']
            success = False

            for invoice_number, amount in payments.items():
                print('Amount::',amount)
                payment = payment_model.create({
                    'ref': invoice_number,
                    'amount': amount,
                    'payment_method_line_id': manual_payment_method_line_id.id,
                })

                if payment:
                    success = True
                    self.write({'file_status_payment': 'processed'})



                if payment.state == 'draft':
                    for pay in payment.search([('state', '=', 'draft')]):

                        pay.write({'payment_method_line_id': manual_payment_method_line_id.id})
                        if pay.state == 'draft':
                            pay.write({'state': 'posted'})
                            invoice = self.env['account.move'].search([('name', '=', invoice_number)], limit=1)
                            if invoice:
                                partner_id = invoice.partner_id
                                pay.write({'partner_id': partner_id})

                        else:
                            raise ValidationError("Payment must be in draft state to be posted")

                    invoice = self.env['account.move'].search([('name', '=', invoice_number)], limit=1)
                    if invoice:
                        partner_id = invoice.partner_id.id
                        payment.write({'partner_id': partner_id})
            if not success:
                self.write({'file_status_payment': 'failed'})


        except Exception as e:
            self.write({'file_status_payment': 'failed'})
            raise e

        print("Processed Invoice Numbers and Amounts:")
        for invoice_number, amount in payments.items():
            print("Invoice Number:", invoice_number, "| Amount:", amount)

        # file_name = werkzeug.utils.secure_filename(self.upload_txt.decode('latin-1'))

    def get_or_create_partner(self, partner_name):
        partner = self.env['res.partner'].search([('name', '=', partner_name)], limit=1)
        if not partner:
            # Create partner if it doesn't exist
            partner = self.env['res.partner'].create({'name': partner_name})
        return partner

    def create_draft_vendor_bill(self, parts, partner_id,payment_reference,date_str):
        try:

            date_str_cleaned = date_str.strip()  # Remove any leading or trailing spaces
            invoice_date = datetime.strptime(date_str_cleaned, "%d%m%y").date()  # Adjust the date format as needed
            vendor_bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': partner_id,
                'state': 'draft',
                'invoice_date': invoice_date,
                'payment_reference':payment_reference,
            })


            print("Draft vendor bill created:", vendor_bill)




            vendor = self.env['res.partner'].search([('name', '=', 'Adesion')], limit=1)
            if not vendor:
                vendor = self.env['res.partner'].create({
                    'name': 'Adesion',
                    # Add other necessary fields for the vendor
                })

            product_name = "RA-Factored"  # Change this to the name of your desired product
            product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': product_name,
                    'detailed_type': 'service',
                    'sale_ok': False,
                    'purchase_ok': True,
                    'seller_ids': [(0, 0, {
                        'partner_id': vendor.id,

                    })],

                })

            # Create the invoice line for the product
            self.env['account.move.line'].create({
                'move_id': vendor_bill.id,
                'product_id': product.id,
                'name': product.display_name,
                'quantity': 1,  # Assuming you want to add one unit of the product
                'price_unit': product.list_price,  # Adjust the price as needed
                # Add other necessary fields for the invoice line
            })

            ri_administrated_name = "RI-Administrated"
            ri_administrated_product = self.env['product.product'].search([('name', '=', ri_administrated_name)],
                                                                          limit=1)
            if not ri_administrated_product:
                ri_administrated_product = self.env['product.product'].create({
                    'name': ri_administrated_name,
                    'detailed_type': 'service',
                    'sale_ok': False,
                    'purchase_ok': True,
                    'seller_ids': [(0, 0, {
                        'partner_id': vendor.id,

                    })],
                    # Add other necessary fields for the product
                })

            # Create the invoice line for product RI-Administrated
            self.env['account.move.line'].create({
                'move_id': vendor_bill.id,
                'product_id': ri_administrated_product.id,
                'name': ri_administrated_product.display_name,
                'quantity': 1,
                'price_unit': ri_administrated_product.list_price,
                # Add other necessary fields for the invoice line
            })

            self.write({'file_status_bills': 'processed'})

        except:
            self.write({'file_status_bills': 'failed'})

    def process_bills(self):

        if not self.file_status_payment:
            raise ValidationError("Please process the payments before processing bills.")

        elif self.file_status_payment == 'failed':
            self.write({'file_status_bills': 'failed'})


        else:
            try:
                file_content = base64.decodebytes(self.file_data).decode("latin-1")


                file_lines = file_content.split("\r\n")
                for line in file_lines:
                    parts = line.split(';')
                    if len(parts) >= 6:
                        date_str = parts[6].strip()
                        print(date_str)
                ra_ri_present = any(
                    "RA" in line.split(';')[0].strip() or "RI" in line.split(';')[0].strip() for line in file_lines)

                if ra_ri_present:
                    # Get or create partner
                    partner_id = self.get_or_create_partner('Adesion').id

                    # Create draft vendor bill
                    self.create_draft_vendor_bill(file_lines, partner_id, self.filename, date_str)

            except Exception as e:
                self.write({'file_status_bills': 'failed'})
                raise e

