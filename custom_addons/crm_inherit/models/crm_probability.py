from odoo import models, fields,api
from odoo.exceptions import ValidationError


class CustomCrmStage(models.Model):
    _inherit = 'crm.stage'

    def init(self):
        # Find the 'Proposition' stage and update its name
        proposition_stage = self.env['crm.stage'].search([('name', '=', 'Proposition')])
        if proposition_stage:
            proposition_stage.write({'name': 'Quotation'})



class CustomCrmLead(models.Model):
    _inherit = 'crm.lead'

    products = fields.Many2one('product.template',string='Product Interested')

    # @api.constrains('stage_id')
    # def _onchange_stage_id(self):
    #     # Update probability based on the selected stage
    #     if self.stage_id:
    #         print('stage', self.stage_id)
    #         if self.stage_id.name == 'New':
    #             self.probability = 0
    #         elif self.stage_id.name == 'Qualified':
    #             self.probability = 25
    #         elif self.stage_id.name == 'Quotation':
    #             self.probability = 75
    #         else:
    #             # Set a default value if the stage doesn't match any conditions
    #             self.probability = 100


    @api.constrains('stage_id')
    def _check_required_fields(self):
        # Add your required field names here
        required_fields = ['expected_revenue', 'partner_id', 'products', 'email_from', 'phone',
                           'user_id', 'date_deadline', 'tag_ids']

        source_stage_name = 'New'  # Replace 'New' with the actual name of the 'New' stage
        destination_stage_name = 'Quotation'  # Replace 'Qualified' with the actual name of the 'Qualified' stage

        source_stage = self.env['crm.stage'].search([('name', '=', source_stage_name)], limit=1)

        destination_stage = self.env['crm.stage'].search([('name', '=', destination_stage_name)], limit=1)

        for record in self:
            # Check if the move is from 'New' to 'Qualified' stage
            if record.stage_id.id == destination_stage.id:
                for field_name in required_fields:
                    if not record[field_name]:
                        raise ValidationError(
                            f"Field '{field_name}' must be filled before moving to the next stage.")

        # for field_name in required_fields:
        #     if field_name in self and not self[field_name]:
        #         raise ValidationError(
        #             f"Field '{field_name}' must be filled before moving to the next stage.")


