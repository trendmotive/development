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


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Human Resource Employee'

    state = fields.Selection([
        ('cook', 'Cook'),
        ('waiter', 'Waiter'),
        ('manager', 'Manager'),
        ('other', 'Other'),
    ], default='other', tracking=True)