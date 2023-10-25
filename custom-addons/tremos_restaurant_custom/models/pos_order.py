import requests
import random
import string
import threading
import logging
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode
from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
import random
import string

_logger = logging.getLogger(__name__)


class RestaurantTable(models.Model):
    _inherit = 'pos.order'
    _description = 'Point of sale extension'

    state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('assigned', 'Assigned To Cook'),
        ('kitchen', 'Being Prepared'),
        ('ready', 'Await Waiter'),
        ('served', 'Meal Served'),
        ('paid', 'Paid'),
        ('done', 'Posted'),
        ('invoiced', 'Invoiced')
    ], default='draft', tracking=True)
    cook = fields.Many2one("hr.employee", string="Cook", readonly=True)
    deadline = fields.Datetime(string="Deadline")
    start_time = fields.Datetime(string="Start Time")
    duration = fields.Integer(string="Durration")
    time_left = fields.Float(string="Time Left", readonly=True)
