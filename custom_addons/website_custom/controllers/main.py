from odoo import http
from odoo.http import request
import base64
# from odoo.addons.mail.wizard import MailComposer
# from odoo.addons.mail.wizard.mail_compose_message import MailComposer




class SignupDetails(http.Controller):

    @http.route('/signup',auth='public',website=True)
    def index(self):
        return request.render('website_custom.signup_details')

class YourController(http.Controller):

    @http.route('/submit_form', type='http', auth='public', website=True,csrf=True)
    def your_controller_method(self, **post):

        name = post.get('name')
        email = post.get('email')
        password = post.get('password')
        print(email)

        user_vals = {
            'name': name,
            'login': email,
            # 'email': email,
            'password': password,

        }

        user = http.request.env['res.users'].sudo().create(user_vals)
        # self.send_email(email)
        self.send_email_with_attachment(email)


        return request.render('website_custom.create_success')


    # This is just sending a simple mail with context named email_values
    # def send_email(self, email):
    #     # Create an instance of the Mail class
    #     mail_obj = http.request.env['mail.mail']
    #
    #     # Compose the email
    #     email_values = {
    #         'subject': "Account creation",
    #         'body_html': 'account created successfully',
    #         'email_to': email,
    #     }
    #
    #     # Send the email
    #     mail_id = mail_obj.create(email_values)
    #     mail_id.send()





# fedp xsnn afvn zylp
# vymj opul zori tlmd



    # This is to send a email with attachment but the attachment is present in Local
    # def send_email_with_attachment(self, email):
    #
    #     env = http.request.env
    #     print("Mail")
    #     mail_subject = "Welcome to Our Website"
    #     mail_body = "Thank you for signing up on our website. Please find attached your welcome letter."
    #
    #     # Replace 'your_attachment_path' with the actual path to your attachment file
    #     attachment_path = '/home/nivetha/Downloads/Hotel Folio.pdf'
    #
    #     attachment_data = {
    #         'name': 'Welcome_Letter.pdf',
    #         'datas': base64.b64encode(open(attachment_path, 'rb').read()).decode('utf-8'),
    #         'res_model': 'res.users',
    #         # 'res_id': user.id,
    #         'type': 'binary',
    #     }
    #
    #     # Create the attachment
    #     attachment = http.request.env['ir.attachment'].sudo().create(attachment_data)
    #
    #     # Send the email with attachment
    #     mail_values = {
    #         'subject': mail_subject,
    #         'body_html': mail_body,
    #         'email_to': email,
    #         'attachment_ids': [(6, 0, [attachment.id])],
    #     }
    #
    #     mail = http.request.env['mail.mail'].sudo().create(mail_values)
    #     mail.send()


    # THis is the function for sending the email with content present in the created Email Template using its XML ID.
    def send_email_with_attachment(self, email):
#
#         env = http.request.env
          mail_template_id = http.request.env.ref( '__export__.mail_template_32_99bcb755')  # Replace 'your_module.email_template_id' with the actual ID or XML ID of your template
          mail_subject = mail_template_id.subject
          mail_body = mail_template_id.body_html


          mail_values = {
              'subject': mail_subject,
              'body_html': mail_body,
              'email_to': email,
              'model': 'res.users',
              'attachment_ids': [(6, 0, mail_template_id.attachment_ids.ids)],}

          mail = http.request.env['mail.mail'].sudo().create(mail_values)
          mail.send()





