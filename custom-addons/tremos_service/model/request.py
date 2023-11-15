import logging
from odoo import fields, models, api, _
from datetime import datetime
import threading

_logger = logging.getLogger(__name__)
SERVICE_TYPES = [
    ('BUY_PARTS', "Purchase Parts"),
    ('NEED_SERVICE', "Provide Car Service"),
]
REQUEST_TYPES = [
    ('INTERNAL', "Internal Request"),
    ('EXTERNAL', "External Request"),
]
STAGES = [
    ('RFQ', "Request for Quotation"),
    ('QUOTATION', "Quotation"),
    ('ORDER_CONFIRM', "Quotation Confirmed"),
    ('SENT_TO_WORKSHOP', "Sent To Workshop"),
    ('SERVICE_START', "Service Started"),
    ('SERVICE_DONE', "Service Complete"),
    ('SERVICE_INVOICED', "Request Invoiced"),
    ('CANCELLED', "Quotation Cancelled"),
    ('PAID', "Paid"),
]
FUEL_TYPES = [
    ('diesel', 'Diesel'),
    ('gasoline', 'Gasoline'),
    ('full_hybrid', 'Full Hybrid'),
    ('plug_in_hybrid_diesel', 'Plug-in Hybrid Diesel'),
    ('plug_in_hybrid_gasoline', 'Plug-in Hybrid Gasoline'),
    ('cng', 'CNG'),
    ('lpg', 'LPG'),
    ('hydrogen', 'Hydrogen'),
    ('electric', 'Electric'),
]


class CustomerRequest(models.Model):
    _name = 'customer.request'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = 'Requests from customers'
    _rec_name = 'partner_id'
    _order = 'sequence'
    @api.model
    def create(self, vals):
        vals.update({
            'sequence': self.env['ir.sequence'].next_by_code('customer.request.request')
        })
        result = super(CustomerRequest, self).create(vals)
        return result

    @api.onchange("service_type", "service_id")
    def create_default_values(self):
        lines = []
        checkList = []
        for rec in self:
            [checkList.append((0, 0, {"list_id": res.id})) for res in
             self.env['vehicle.request.check.list'].search([("is_required", "=", True)])]
            rec.request_line_ids = False
            if rec.service_type == "NEED_SERVICE" and rec.service_id:
                [lines.append((0, 0, {
                    "product_id": res.product_id,
                    "quantity": res.quantity,
                    "qty_available": res.qty_available,
                    "total_price": res.total_price,
                    "tax_ids": res.tax_ids,
                    "account_id": res.account_id.id,
                })) for res in rec.service_id.category_line_ids]
                rec.write({
                    'request_line_ids': lines,
                    'check_lst_ids': checkList
                })

    @api.depends('request_line_ids.quantity', 'request_line_ids.default_price', 'request_line_ids.tax_ids')
    def _compute_amount(self):
        for record in self:
            total_price = 0.0
            for line in record.request_line_ids:
                taxes = line.tax_ids.compute_all(
                    line.default_price, line.currency_id, line.quantity, product=line.product_id
                )
                total_price += taxes['total_excluded']

            record.update({
                'total_price': total_price,
            })
    state = fields.Selection(STAGES, default='RFQ', tracking=True)
    sequence = fields.Char(string="Sequence", readonly=True)
    image_128 = fields.Binary(readonly=True, related="vehicle_id.image_128")
    description = fields.Char(string="Description", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, tracking=True)
    warrant_provider_id = fields.Many2one("res.partner", string="Warrant Company", tracking=True,default=71)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle",tracking=True)
    request_type = fields.Selection(REQUEST_TYPES, default='EXTERNAL', string="Request Type", required=True,
                                    tracking=True)
    service_type = fields.Selection(SERVICE_TYPES, default='NEED_SERVICE', required=True, tracking=True)
    model_id = fields.Many2one("fleet.vehicle.model", string="Model", related="vehicle_id.model_id", tracking=True)
    brand_id = fields.Many2one("fleet.vehicle.model.brand", string="Make", related="vehicle_id.model_id.brand_id",
                               tracking=True)
    next_date = fields.Datetime(string="Next Service Date", default=datetime.today(), tracking=True)
    request_date = fields.Datetime(string="Reuqest Date", default=datetime.today(), tracking=True)
    # odometer_reading = fields.Float(string="Odometer Reading", tracking=True)
    # fuel_reading = fields.Float(string="Fuel Reading", tracking=True)
    chassis_number = fields.Char(string="Chassis Number", readonly=True, related="vehicle_id.vin_sn", tracking=True)
    license_plate = fields.Char(string="License Number", readonly=True, related="vehicle_id.license_plate",
                                tracking=True)
    vin_number = fields.Char(string="Vin Number", readonly=True, related="vehicle_id.vin_number", tracking=True)
    model_year = fields.Char(string="Model Year", readonly=True, related="vehicle_id.model_year", tracking=True)
    color = fields.Char(string="Color", related="vehicle_id.color", tracking=True)
    fuel_type = fields.Selection(FUEL_TYPES, related="vehicle_id.fuel_type", tracking=True)
    acquisition_date = fields.Date(string="Registration Date", related="vehicle_id.acquisition_date", tracking=True)
    company_id = fields.Many2one("res.company", string='Company',default=lambda self: self.env.user.company_id.id)
    service_id = fields.Many2one("vehicle.service.category", string='Service Type', tracking=True)
    payment_term_id = fields.Many2one("account.payment.term", string='Payment Terms', tracking=True)
    is_true = fields.Boolean(string="Is True", default=True, readonly=True)
    request_line_ids = fields.One2many('vehicle.service.category.lines', 'vehicle_request_id',
                                       string="Related Products", tracking=True)
    check_lst_ids = fields.One2many('vehicle.request.checklisting', 'request_id', string="Check Listing", tracking=True)
    has_warrant = fields.Boolean(string="Has Warrant", default=False)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    mechanic_id = fields.Many2one("hr.employee", string="Mechanic Incharge")
    instructions = fields.Char(string="Instructions to Mechanic")
    service_start = fields.Datetime(string="Service Start",readonly=True,tracking=True)
    service_end = fields.Datetime(string="Service End",readonly=True,tracking=True)
    duration = fields.Float(string='Duration (hours)', compute='_compute_duration', store=True,tracking=True)
    is_visible=fields.Many2one(string="Is Visible")
    @api.onchange("state","service_type")
    def is_it_visible(self):
        for rec in self:
            if self.state=="ORDER_CONFIRM" and rec.service_type=="BUY_PARTS":
                rec.is_visible=True
    @api.depends("service_start","service_end")
    def _compute_duration(self):
        for record in self:
            if record.service_start and record.service_end:
                duration_hours = (record.service_end - record.service_start).total_seconds() / 3600.0
                record.duration = duration_hours
            else:
                record.duration = 0.0
    def action_create_quotation(self):
        for rec in self:
            if rec.state == "RFQ":
                rec.write({"state": "QUOTATION"})
    def action_confirm_client_quotations(self):
        for rec in self:
            if rec.state == "QUOTATION":
                rec.write({"state": "ORDER_CONFIRM"})
    def action_send_to_workshop(self):
        for rec in self:
            if rec.state == "ORDER_CONFIRM" and rec.service_type=="NEED_SERVICE":
                rec.write({"state": "SENT_TO_WORKSHOP"})
            if rec.state == "ORDER_CONFIRM" and rec.service_type=="BUY_PARTS":
                    rec._prepare_invoice_values()
    def action_start_service(self):
        for rec in self:
            if rec.state == "SENT_TO_WORKSHOP":
                rec.write({"state": "SERVICE_START","service_start":fields.Datetime.now()})
    def action_service_done(self):
        for rec in self:
            if rec.state == "SERVICE_START":
                rec.write({"state": "SERVICE_DONE","service_end":fields.Datetime.now()})

    def action_create_invoice(self):
        for rec in self:
            if rec.state == "SERVICE_DONE":
                rec._prepare_invoice_values()
            if rec.state == "SERVICE_INVOICED":
                rec.write({"state": "PAID"})
    def action_mark_done(self):
        for rec in self:
            if rec.state != "PAID":
                rec.write({"state": "PAID"})
    
    def action_reset_request(self):
        for rec in self:
            if rec.state != "CANCELLED":
                rec.write({"state": "CANCELLED"})
            if rec.state == "CANCELLED":
                rec.write({"state": "RFQ"})

    def _prepare_invoice_values(self):
        move_lines=[]
        [move_lines.append((0,0,{
            "product_id":rec.warrant_provider_id.id if self.has_warrant else rec.partner_id.id,
            "account_id":rec.account_id.id,
            "quantity":rec.quantity,
            "price_unit":rec.default_price,
            "tax_ids":rec.tax_ids,
        })) for rec in self.request_line_ids]
        move_object=self.env["account.move"].create({
            "partner_id":self.partner_id.id,
            "invoice_date":self.acquisition_date,
            "invoice_payment_term_id":self.payment_term_id.id,
            "move_type":"out_invoice",
            "invoice_user_id":self.env.user.id,
            "invoice_line_ids":move_lines
        })
        if move_object:
            if self.state=="ORDER_CONFIRM":
                self.write({"state": "SERVICE_INVOICED"})
                move_object.action_post()
            if self.state =="SERVICE_DONE":
                self.write({"state": "SERVICE_INVOICED"})
                move_object.action_post()
        