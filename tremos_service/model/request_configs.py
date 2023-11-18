import logging
from odoo import fields, models, api, _
from datetime import datetime

_logger = logging.getLogger(__name__)
SERVICE_FREQUENCY = [
    ('MONTHLY', "Monthly Check Service"),
    ('YEARLY', "Yearly Check Service"),
    ('OTHER', "Other Service"),

]


class VehicleServiceCategory(models.Model):
    _name = 'vehicle.service.category'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Vehicle Service Category'

    name = fields.Char(string="Name", tracking=True)
    category_line_ids = fields.One2many('vehicle.service.category.lines', 'vehicle_service_category_id',
                                        string="Related Products")
    service_freq = fields.Selection(SERVICE_FREQUENCY, default='OTHER', required=True)
    company_id = fields.Many2one("res.company", string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', required=True)
    total = fields.Monetary(string="Default Amount", compute="_compute_default_total", store=True)
    is_true = fields.Boolean(string="Is True", default=False, readonly=True)

    @api.model
    def _compute_default_total(self):
        total = 0.00
        for rec in self.category_line_ids:
            total += rec.default_price
        self.total = total


class CustomerConfigsLines(models.Model):
    _name = 'vehicle.service.category.lines'

    # @api.onchange('quantity', 'default_price')
    # def _get_total_per_line(self):
    #     total=0.00
    #     for record in self:
    #         if record.quantity and record.default_price:
    #             total =record.quantity * record.default_price
    #     return total
    @api.depends('quantity', 'default_price', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            tax_results = self.env['account.tax'].search([("id",'=',line.tax_ids.id)])
            amount_value=((tax_results.amount+100)/100 * line.default_price)*line.quantity if tax_results else line.default_price * line.quantity
            line.update({
                'total_price': amount_value,
            })

    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    min_price = fields.Float(string="Minimum Price", default=1.0)
    max_price = fields.Float(string="Maximum Price", default=1.0)
    total_price = fields.Float(string="Total Price", default=1.0, readonly=True,store=True)
    qty_available = fields.Float(string="Quantity Available",related="product_id.qty_available")
    default_price = fields.Float(string="Price", default=1.0)
    account_id = fields.Many2one("account.account", string="Account")
    vehicle_service_category_id = fields.Many2one('vehicle.service.category', string="Vehicle Service Category")
    vehicle_request_id = fields.Many2one('customer.request', string="Vehicle Request Lines")
    tax_ids = fields.Many2one("account.tax",string="Tax")
