from odoo import models,fields,api

class AccountingPayments(models.Model):
    _inherit = 'account.payment'

    def unlink(self):
        for payment in self:
            invoice = self.env['account.move'].search([('name', '=', payment.ref)], limit=1)
            if invoice:
                # Check if there are any other payments associated with the invoice
                other_payments = self.env['account.payment'].search([
                    ('ref', '=', invoice.name),
                    ('id', '!=', payment.id),  # Exclude the current payment
                    ('state', '!=', 'draft'),  # Exclude payments in draft state
                ])
                if not other_payments:
                    invoice.write({'status': 'to_upload'})
        return super(AccountingPayments, self).unlink()

class AccountingInvoices(models.Model):
    _inherit = 'account.move'

    # status = fields.Char(string="Adesion Status")
    status = fields.Selection([
        ('to_upload', 'Adhesion status yet to upload'),
        ('factored', 'Factored'),
        ('admin_started', 'Administrated')
    ], string="Adhesion Status", default='to_upload', readonly=True)

