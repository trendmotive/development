# import threading
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)
SALE_TAX_CODE = [
    ('A_CODE', "Sale Tax Code A"),
    ('C_CODE', "Sale Tax Code C"),
    ('D_CODE', "Sale Tax Code D")
]

class Move(models.Model):
    _inherit = "account.move"
    sale_tax_code = fields.Selection(SALE_TAX_CODE, default='A_CODE',required=True)
    move_tax_ids=fields.One2many("account.move.tax.items",'items_tax_ids',readonly=True)


    @api.depends('invoice_line_ids')
    def calculate_tax_ids(self):
        tax_values = {
        "A_CODE": {"tax": 0, "tax_amount": 0, "net_amount": 0, "gross": 0},
        "C_CODE": {"tax": 0, "tax_amount": 0, "net_amount": 0, "gross": 0},
        "D_CODE": {"tax": 0, "tax_amount": 0, "net_amount": 0, "gross": 0},
        }
        for rec in self.invoice_ine_ids:
            tax_code = rec.product_id.sale_tax_code
            tax_values_for_code = tax_values.get(tax_code)

            if tax_values_for_code:
                tax = rec.tax_ids.amount
                tax_amount = rec.price_subtotal - rec.price_unit * rec.quantity
                net_amount = rec.price_unit * rec.quantity
                gross = rec.price_subtotal

                tax_values_for_code["tax"] += tax
                tax_values_for_code["tax_amount"] += tax_amount
                tax_values_for_code["net_amount"] += net_amount
                tax_values_for_code["gross"] += gross
        tax_values_list = list(tax_values.values())
        _logger.error(tax_values_list)
        _logger.error("TESTING THE VALUES FOR THE USERS")
class TaxLinesItems(models.Model):
    _name = 'account.move.tax.items'

    items_tax_ids= fields.Many2one('account.move',readonly=True)
    sale_tax_code = fields.Selection(SALE_TAX_CODE,readonly=True)
    tax_ids=fields.Many2one('account.tax',string="Tax %",readonly=True)
    total_net=fields.Float(string="Total Net",readonly=True)
    total_tax=fields.Float(string="Total Tax",readonly=True)
    total_gross=fields.Float(string="Total Gross",readonly=True)

