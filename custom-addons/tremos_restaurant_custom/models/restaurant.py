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
    _inherit = 'restaurant.table'
    _description = 'Partner wizard'

    @api.model
    def create(self, vals):
        vals.update({'sequence': self.env['ir.sequence'].next_by_code('restaurant.table')})
        result = super(RestaurantTable, self).create(vals)
        return result

    sequence = fields.Char(string="Seq", readonly=True)
