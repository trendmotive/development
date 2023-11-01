from odoo import http
from odoo.http import request, Response
from odoo.tools import float_is_zero, float_compare
import json
import logging
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class SmsResponse(http.Controller):
    @http.route('/sms/gateway', auth='public', type='json', csrf=False, method=['POST'])
    def getsmsResponse(self, **kw):
        response = json.loads(request.httprequest.data)
        data = response['data']
        if data:
            existingSms = request.env["sms.sms"].sudo().search([("id", "=", data['source_id'])])
            if data['delivery_report'] == "DeliveredToTerminal" and existingSms:
                existingSms.write({"state": "sent"})
            if data['delivery_report'] == "SenderName Blacklisted":
                existingSms.write({"state": "error"})
            if data['delivery_report'] == "SENT":
                existingSms.write({"state": "outgoing"})
            if data['delivery_report'] == "DeliveryImpossible":
                existingSms.write({"state": "error"})
            if existingSms.mailing:
                existingTrace = request.env["mailing.trace"].sudo().search([("mass_mailing_id", "=", existingSms.mailing.id)])
                if existingTrace:
                    if data['delivery_report'] == "DeliveredToTerminal" and existingTrace:
                        existingTrace.write({"trace_status": "sent"})
                    if data['delivery_report'] == "SenderName Blacklisted" and existingTrace:
                        existingTrace.write({"trace_status": "bounce"})
                    if data['delivery_report'] == "SENT" and existingTrace:
                        existingTrace.write({"trace_status": "outgoing"})
                    if data['delivery_report'] == "DeliveryImpossible" and existingTrace:
                        existingTrace.write({"trace_status": "bounce"})
        return True
