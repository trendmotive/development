import requests
# import threading
import logging
from odoo import fields, models, api,_
from odoo.exceptions import ValidationError, UserError
import random
import string
_logger = logging.getLogger(__name__)
PROVIDERS = [
    ('ujumbesms', "UjumbeSMS"),
    ('africastalking', "Africa's Talking")
]
baseUrl=""
def _sanitize_phone_number(number):
    phone = number.strip('-')
    phone = phone.replace(" ", "")

    if phone.startswith("7"):
        phone = "254%s" % phone
    if phone.startswith('+254'):
        phone = "%s" % phone[1:]
    if phone.startswith('0'):
        phone = "254%s" % phone[1:]
    return phone

class SmsProviderGateway(models.Model):
        _name = 'sms.provider.gateway'
        _inherit = ["mail.thread", 'mail.activity.mixin']
        _description = 'SMS Provider Gateway'
        _order = 'sequence'

        provider = fields.Selection(PROVIDERS, default='ujumbesms', required=True)
        sequence = fields.Integer(default=10)
        name = fields.Char("Name", required=True)
        active=fields.Boolean(string="Active",default=False)
        # UJUMBESMS REQUIREMENTS
        api_key=fields.Char(string="Api Key")
        email = fields.Char(string="Account Email")
        sms_left=fields.Char(string="Sms Remaining",readonly=True)

        def sendSmsNotification(self,obj_data=None,messageId=None):
            payload={}
            if self.provider == 'ujumbesms':
                if obj_data:
                    url = "https://ujumbesms.co.ke/api/messaging"
                    payload = {
                        "data": [
                            {
                                "message_bag": {
                                    "numbers": obj_data['numbers'],
                                    "message": obj_data['message'],
                                    "sender": self.env.company.name,
                                    "source_id": obj_data['source_id'],
                                }
                            }
                        ]
                    }
                if messageId:
                    messageExist=self.env['sms.sms'].search([('id','=',messageId)])
                    payload = {
                        "data": [
                            {
                                "message_bag": {
                                    "numbers": messageExist.partner_id.mobile or messageExist.partner_id.phone,
                                    "message": messageExist.body,
                                    "sender": self.env.company.name,
                                    "source_id": messageExist.number,
                                }
                            }
                        ]
                    }
                headers = self.get_request_headers()
                
                response = self.send_sms_request(url, headers, payload)
                _logger.error(response.text)
        def get_request_headers(self):
            return {
                'X-Authorization': self.api_key,
                'email': self.email,
                'Content-Type': 'application/json',
            }

        def send_sms_request(self, url, headers, payload):
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Error sending SMS request: {str(e)}")
                return None

        def activateProvider(self):
            for rec in self:
                if rec.active:
                    rec.write({"active":False})
                else:
                    rec.write({"active":True})

        # def smsHistory(self, response, partner_id, obj_data):
        #     _logger.error(response)
        #     if response and response.status_code == 200:
        #         parsed_data = response.json()
        #         _logger.error(partner_id)
        #         _logger.error(parsed_data)
        #         if parsed_data.get('status', {}).get('type') == "success":
        #             obj = {
        #                 "state": "sent",
        #                 "number": None,
        #                 "partner_id": partner_id.id if partner_id else None,
        #                 "body": obj_data['message'],
        #             }
        #             sms_history = self.env['sms.sms'].sudo().create(obj)
        #     return True


class Mailing(models.Model):
    _inherit = 'mailing.mailing'


    def sction_send_sms_now(self):
        letters = string.ascii_letters
        random_string = ''.join(random.choice(letters) for _ in range(10))
        sms_provider=self.env['sms.provider.gateway'].sudo().search([("active","=",True)],limit=1)
        for rec in self.contact_list_ids.contact_ids:
            _logger.error(rec.mobile)
            obj_data={
                "numbers": rec.mobile,
                "message": self.body_plaintext,
                "source_id": random_string,
            }
            if sms_provider:
                sms_provider.sendSmsNotification(obj_data)
                mail_trace=self.env["mailing.trace"].sudo().create({
                    "mass_mailing_id":self.id,
                    "sms_number":rec.mobile,
                    "medium_id":self.medium_id.id,
                    "source_id": self.source_id.id,
                    "trace_status":"sent",
                    "model":rec.id,
                    "res_id":self.id,
                    "trace_type":"sms"
                })
                self.write({"state":"sending"})
            else:
                raise ValidationError("You Have not set an sms provider")
        self.write({"state":"done"})
        return True

class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'
    _description = 'Send SMS Wizard'

    def action_send_sms(self):
        partner_ids = self.env.context.get('active_ids', [])
        records = self.env['res.partner'].search([('id','in',partner_ids)])
        provider=self.env['sms.provider.gateway'].search([('active','=',True)])
        letters = string.ascii_letters
        random_string = ''.join(random.choice(letters) for _ in range(20))
        if provider:
            if partner_ids:
                for rec in records:
                    obj_data = {
                            "numbers": rec.mobile or rec.phone,
                            "message": self.body,
                            "source_id": random_string
                        }
                    provider.sendSmsNotification(obj_data)
            else:
                obj_data = {
                "numbers": self.recipient_single_number_itf,
                "message": self.body,
                "source_id": random_string
                }
                provider.sendSmsNotification(obj_data)
            return True
        else:
            if self.composition_mode in ('numbers', 'comment'):
                if self.comment_single_recipient and not self.recipient_single_valid:
                    raise UserError(_('Invalid recipient number. Please update it.'))
                elif not self.comment_single_recipient and self.recipient_invalid_count:
                    raise UserError(_('%s invalid recipients', self.recipient_invalid_count))
            self._action_send_sms()
            return False