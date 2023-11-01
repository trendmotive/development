import requests
# import threading
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import random
from dateutil.relativedelta import relativedelta

from datetime import datetime
import string

_logger = logging.getLogger(__name__)
INSTTYPE = [
    ('installment', "Installment"),
    ('downpayment', "DownPayment")
]
PAIDSTATUS = [
    ('unpaid', "UnPaid"),
    ('partial', "Partial"),
        ('paid', "Paid")
]


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = "Register Payment"

    def action_create_payments(self):
        active_id = self.env.context.get('active_ids', [])
        payments = self._create_payments()

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        move_id=self.env["account.move"].search("id","=",active_id)
        if move_id and len(move_id.pay_ids)>0:
            move_id.update_unpaid_payments()
        return action
class AccoutMove(models.Model):
    _inherit = 'account.move'
    pay_ids=fields.One2many("move.payment.schedule","invoice_id",string="mailing",readonly=True)
    include_schedule=fields.Boolean(string="Add Payment Schedule",default=False,)
    payment_start_date=fields.Date(string="Payment Start Date")
    payment_period=fields.Integer(string="Period (Months)",default=False)
    see_me=fields.Boolean(string="See me",default=False)
    def clear_lines(self):
        """This automatically create the installment for the remaining amount to be paid"""
        for move_id in self:
               move_id.pay_ids.sudo().unlink()
        self.write({'see_me':False})
        return True
    def update_unpaid_payments(self):
        for rec in self:
            unpaid_installments = rec.pay_ids.filtered(lambda x: x.status !="paid")
            new_payment_amount = rec.amount_paid  # Replace with your desired new payment amount
            remaining_balance = 0
            if unpaid_installments:
                total_remaining_balance = remaining_balance + (new_payment_amount - sum(abs(inst.amount_paid) for inst in rec.pay_ids))
                for installment in unpaid_installments:
                    if total_remaining_balance == 0:
                        break
                    if total_remaining_balance >= installment.amount_total-installment.amount_paid:
                        installment.write({'amount_paid': installment.amount_total-installment.amount_paid,"status":"paid"})
                        total_remaining_balance -= installment.amount_total-installment.amount_paid
                    else:
                        installment.write({'amount_paid': total_remaining_balance,"status":"partial"})
                        total_remaining_balance = 0
                rec.installments.filtered(lambda x: not x.paid).update({'paid': False})
            else:
                remaining_balance = new_payment_amount
        """This automatically create the installment for the remaining amount to be paid"""
        for move_id in self:
               move_id.pay_ids.sudo().unlink()
        self.write({'see_me':False})
        return True
    def update_payment(self):
        for rec in self:
            amount_paid=rec.amount_paid

    def generate_payment_schedule(self):
        """This automatically create the installment for the remaining amount to be paid"""
        paymentPlan=[]
        for move_id in self:
            if move_id.include_schedule:
                date_start = datetime.strptime(str(move_id.payment_start_date), '%Y-%m-%d')
                amount = move_id.amount_residual / move_id.payment_period
                for i in range(1, move_id.payment_period + 1):
                    self.env['move.payment.schedule'].create(
                        {
                        'payment_date': date_start,
                        'description': "installment",
                        'amount_total':amount,
                        'amount_paid': 0.00,
                        'amount_balance': amount,
                        'currency_id': move_id.currency_id.id,
                        'invoice_id':move_id.id,
                        'amount_balance': amount
                        }
                    
                    )
                    date_start = date_start + relativedelta(months=1)
            
            else:
                raise UserError("Please Clear Lines Before Generating")
                # loan._compute_loan_amount()

        return self.write({'see_me':True})

class PaymentSchedule(models.Model):
    _name = 'move.payment.schedule'

    invoice_id=fields.Many2one("account.move",string="mailing")
    payment_date=fields.Date(string="Payment Date")
    currency_id=fields.Many2one('res.currency',related="invoice_id.currency_id")
    amount_total=fields.Monetary(string="Amount")
    amount_paid=fields.Monetary(string="Paid")
    amount_balance=fields.Monetary(string="balance")
    description= fields.Selection(INSTTYPE, default='installment', required=True)
    status= fields.Selection(PAIDSTATUS, default='unpaid', required=True)


    
