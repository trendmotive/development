import logging
from odoo import fields, models, api, _
from datetime import datetime
_logger = logging.getLogger(__name__)
class VehicleCeckList(models.Model):
    _name= 'vehicle.request.check.list'

    name=fields.Char(string="Name")
    is_required=fields.Boolean(string="Is Required?")


class CeckListing(models.Model):
    _name= 'vehicle.request.checklisting'


   
    list_id=fields.Many2one("vehicle.request.check.list",required=True)
    request_id=fields.Many2one("customer.request")
    quantity=fields.Integer(string="Reading")
    is_checked=fields.Boolean(string="Item Checked",default=False,required=True)
