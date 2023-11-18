import logging
from odoo import fields, models, api, _
from datetime import datetime
_logger = logging.getLogger(__name__)
class FleetVehicle(models.Model):
    _inherit= 'fleet.vehicle'

    vin_number=fields.Char(string="Vin Number")
    image_128 = fields.Binary(readonly=True)


class Users(models.Model):
    _inherit= 'res.users'

    location_id=fields.Many2one("stock.location",string="Allowed Location",tracking=True)