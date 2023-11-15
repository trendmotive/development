import requests
# import threading
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import random
import string

_logger = logging.getLogger(__name__)
SALE_TAX_CODE = [
    ('A_CODE', "Sale Tax Code A"),
    ('C_CODE', "Sale Tax Code C"),
    ('D_CODE', "Sale Tax Code D")
]

class Product(models.Model):
    _inherit = "product.product"
    sale_tax_code = fields.Selection(SALE_TAX_CODE, default='A_CODE',required=True,tracking=True)

