import requests
# import threading
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import random
import string

_logger = logging.getLogger(__name__)
PROVIDERS = [
    ('ujumbesms', "UjumbeSMS"),
    ('africastalking', "Africa's Talking")
]
url = "https://ujumbesms.co.ke/api/messaging"
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
    active = fields.Boolean(string="Active", default=False)
    # UJUMBESMS REQUIREMENTS
    api_key = fields.Char(string="Api Key")
    email = fields.Char(string="Account Email")
    sms_left = fields.Char(string="Sms Remaining", readonly=True)

    def sendSmsNotification(self, obj_data=None, messageId=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        payload = {}
        if self.provider == 'ujumbesms':
            if obj_data:
                messageToBeSent = self.env['sms.sms'].create({
                    "mailing":obj_data["custom_id"] if obj_data["custom_id"] else None,
                    "number": obj_data['numbers'],
                    "partner_id": self.env['res.partner'].search([("mobile", "=", obj_data['numbers']), ("phone", "=", obj_data['numbers'])]).id if self.env['res.partner'].search([("mobile", "=", obj_data['numbers']), ("phone", "=", obj_data['numbers'])]) else None, "body": obj_data['message']})
                payload = {
                    "data": [
                        {
                            "message_bag": {
                                "numbers": obj_data['numbers'],
                                "message": obj_data['message'],
                                "sender": self.env.company.name,
                                "source_id": messageToBeSent.id,
                                "delivery_report_endpoint": "http://143.198.156.218:8069/sms/gateway"
                            }
                        }
                    ]
                }
            if messageId:
                messageExist = self.env['sms.sms'].search([('id', '=', messageId)])
                payload = {
                    "data": [
                        {
                            "message_bag": {
                                "numbers": messageExist.number,
                                "message": messageExist.body,
                                "sender": self.env.company.name,
                                "source_id": messageExist.id,
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
                rec.write({"active": False})
            else:
                rec.write({"active": True})


class Mailing(models.Model):
    _inherit = 'mailing.mailing'
    sms_ids=fields.One2many("sms.sms","mailing",string="mailing")
    
    def sction_send_sms_now(self):
        letters = string.ascii_letters
        random_string = ''.join(random.choice(letters) for _ in range(10))
        sms_provider = self.env['sms.provider.gateway'].sudo().search([("active", "=", True)], limit=1)
        for rec in self.contact_list_ids.contact_ids:
            obj_data = {
                "numbers": rec.mobile,
                "message": self.body_plaintext,
                "custom_id": self.id,
            }
            if sms_provider:
                sms_provider.sendSmsNotification(obj_data)
                mail_trace = self.env["mailing.trace"].sudo().create({
                    "mass_mailing_id": self.id,
                    "sms_number": rec.mobile,
                    "medium_id": self.medium_id.id,
                    "source_id": self.source_id.id,
                    "trace_status": "sent",
                    "model": rec.id,
                    "res_id": self.id,
                    "trace_type": "sms"
                })
                self.write({"state": "in_queque"})
            else:
                raise ValidationError("You Have not set an sms provider")
        self.write({"state": "done"})
        return True


class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'
    _description = 'Send SMS Wizard'

    def action_send_sms(self):
        partner_ids = self.env.context.get('active_ids', [])
        records = self.env['res.partner'].search([('id', 'in', partner_ids)])
        provider = self.env['sms.provider.gateway'].search([('active', '=', True)])
        letters = string.ascii_letters
        random_string = ''.join(random.choice(letters) for _ in range(20))
        if provider:
            if partner_ids:
                for rec in records:
                    obj_data = {
                        "numbers": rec.mobile or rec.phone,
                        "message": self.body,
                        "source_id": random_string,
                        "custom_id":None
                    }
                    provider.sendSmsNotification(obj_data)
            else:
                obj_data = {
                    "numbers": self.recipient_single_number_itf,
                    "message": self.body,
                    "source_id": random_string,
                    "custom_id":None
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



class SmsSms(models.Model):
    _inherit = "sms.sms"

    mailing=fields.Many2one("mailing.mailing",string="mailing")
    def send(self, unlink_failed=False, unlink_sent=True, auto_commit=False, raise_exception=False):
        """ Main API method to send SMS.
          :param unlink_failed: unlink failed SMS after IAP feedback;
          :param unlink_sent: unlink sent SMS after IAP feedback;
          :param auto_commit: commit after each batch of SMS;
          :param raise_exception: raise if there is an issue contacting IAP;
        """
        customProvider = self.env['sms.provider.gateway'].search([("active","=",True)])
        if customProvider:
            customProvider.sendSmsNotification(messageId=self.id)
            self.write({"state":"sent"})
        else:
            self = self.filtered(lambda sms: sms.state == 'outgoing')
            for batch_ids in self._split_batch():
                self.browse(batch_ids)._send(unlink_failed=unlink_failed, unlink_sent=unlink_sent, raise_exception=raise_exception)
                # auto-commit if asked except in testing mode
                if auto_commit is True and not getattr(threading.current_thread(), 'testing', False):
                    self._cr.commit()

