from odoo import models, fields,api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Medicines'

    medicine_type_id = fields.Many2one('medicine.type', string='Medicine Type')
    category_id = fields.Many2one('product.category', string='Medicine Category')
    medicine_company_id = fields.Many2one('medicine.company', string='Medicine Company')
    expiry_date = fields.Date(string='Expiry Date')
    expiry_period = fields.Integer(string="Expiry period",compute="compute_expire_period")
    expiry_type = fields.Char(string="Exp_Type",default="months")

    @api.onchange(category_id)
    def compute_expire_period(self):
        for record in self:
            print(record.category_id.name)
            if record.category_id and record.category_id.name == 'Excipent':
                 expiry_period = 12
            elif record.category_id.name == 'Active':
                expiry_period = 6
            else:
                expiry_period = 0
            record.expiry_period = expiry_period


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Medicines'

    # medicine_type_id = fields.Many2one('medicine.type', string='Medicine Type')
    # category_id = fields.Many2one('product.category', string='Medicine Category')
    # medicine_company_id = fields.Many2one('medicine.company', string='Medicine Company')
    # expiry_date = fields.Date(string='Expiry Date')
    medicine_type_id = fields.Many2one(related='product_tmpl_id.medicine_type_id', string='Medicine Type',
                                       store=True)
    category_id = fields.Many2one(related='product_tmpl_id.category_id', string='Medicine Category',
                                  store=True)
    medicine_company_id = fields.Many2one(related='product_tmpl_id.medicine_company_id',
                                          string='Medicine Company', store=True)
    expiry_date = fields.Date(related='product_tmpl_id.expiry_date', string='Expiry Date', store=True)
