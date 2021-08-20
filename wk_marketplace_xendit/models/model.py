# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)

import json
import requests

class XenditSellerAccounts(models.Model):
    _name = "xendit.seller.accounts"
    _description = "Seller Xendit Accounts"
    _rec_name = "account_number"

    def name_get(self):
        result = []
        for record in self:
            name = "%s (%s-%s)" % (record.channel_type, record.channel_code, record.account_number)
            name = name[0].upper()+name[1:]
            result.append((record.id, name))
        return result

    channel_type = fields.Selection([('bank','Bank'),('wallet','E-Wallet')], string="Account Type", required=True)
    channel_code = fields.Char(string="Account Code", required=True)
    account_holder_name = fields.Char(string="Account Holder Name", required=True)
    account_number = fields.Char(string="Account Number", required=True)
    seller_id = fields.Many2one('res.partner', string="Seller", domain="[('seller','=', True)]", required=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    enable_xendit_payments = fields.Boolean(string="Accept Xendit Payments")
    xendit_email = fields.Char(string="Xendit Email")
    xendit_public_profile = fields.Char(string="Business Description")
    xendit_account_id = fields.Char(string="Account ID")
    xendit_account_status = fields.Char(string="Account Status")
    seller_xendit_account_ids = fields.One2many('xendit.seller.accounts', 'seller_id', string="Xendit Accounts")

    @api.onchange('enable_xendit_payments')
    def _set_default_xendit_email(self):
        if self.enable_xendit_payments and not self.xendit_email and self.email:
            self.xendit_email = self.email

    def create_xendit_subaccount(self):
        self.ensure_one()
        if not self.xendit_email:
            raise Warning(_("Email is required for creating a subaccount on xendit."))
        if not self.xendit_public_profile:
            raise Warning(_("Business description is required for creating a subaccount on xendit."))
        acquirer_obj = self.env['payment.acquirer'].search(['|',('provider','=','xendit_cards'),('provider','=','xendit_ewallets')], limit=1)
        key = acquirer_obj.get_encrpt_secret_key()
        headers = {
            "content-type" : "application/json",
            "Authorization" : "Basic "+key
        }
        url = "https://api.xendit.co/v2/accounts"
        data = {
            "email" : self.xendit_email,
            "type": "OWNED",
            "public_profile": {
                "business_name": self.xendit_public_profile,
            }
        }
        data = json.dumps(data)
        result = requests.post(url, data=data, headers=headers)
        result = result.json()
        if result.get('id'):
            self.sudo().write({
                'xendit_account_id': result['id'],
                'xendit_account_status': result['status']
            })
        else:
            error_message = result.get('message')
            raise Warning(error_message)

class SellerPayment(models.Model):
    _inherit = 'seller.payment'

    is_xendit_payment = fields.Boolean(string="Is Xendit Payment?")
    xendit_disbursement_id = fields.Char(string="Disbursement ID")
    xendit_disbursement_status = fields.Char(string="Disbursement Status")
    acquirer_id = fields.Many2one('payment.acquirer')
    xendit_channel_code = fields.Char(string="A/c Code")
    xendit_account_holder_name = fields.Char(string="A/c Holder Name")
    xendit_account_number = fields.Char(string="Xendit A/c Number")
    xendit_disbursement_failed_msg = fields.Char(string="Failed Message")
    xendit_unique_key = fields.Integer("Xendit Unique Key", default=0)

    def update_failed_xendit_seller_disbursement(self, msg):
        self.ensure_one()
        self.xendit_disbursement_status = "FAILED"
        self.xendit_disbursement_failed_msg = msg

    def update_success_xendit_seller_disbursement(self):
        self.ensure_one()
        self.xendit_disbursement_status = "COMPLETED"
        self.do_Confirm()
        self.invoice_id.action_post()
        journal_id = self.acquirer_id.journal_id if self.acquirer_id and self.acquirer_id.journal_id else (self.invoice_id.journal_id if self.invoice_id else False)
        account_payment_method_id = journal_id.outbound_payment_method_ids[0] if journal_id and journal_id.outbound_payment_method_ids else False
        payment_vals = {
            'payment_type': "outbound",
            'partner_type': "seller",
            'partner_id': self.seller_id.id,
            'communication': self.name,
            'journal_id': journal_id.id if journal_id else False,
            'payment_method_id':  account_payment_method_id.id if account_payment_method_id else False,
            'invoice_ids': [(5,), (4, self.invoice_id.id)],
            'amount': abs(self.payable_amount),
        }
        payment_obj = self.env['account.payment'].create(payment_vals)
        payment_obj.post()
        self.write({'state': "posted"})

    def create_xendit_seller_disbursement(self, account_id=None, retry=False):
        for rec in self:
            seller = rec.seller_id
            acquirer_obj = rec.acquirer_id
            currency_id = self.currency_id
            if currency_id and currency_id.name != "PHP":
                raise ValidationError(_('Currency(%s) not supported by Xendit.' % currency_id.name))
            if retry and rec.xendit_disbursement_id and rec.xendit_disbursement_status == 'FAILED':
                rec.xendit_unique_key += 1
                account_holder_name = rec.xendit_account_holder_name
                account_number = rec.xendit_account_number
                channel_code = rec.xendit_channel_code
            elif account_id:
                account_holder_name = account_id.account_holder_name
                account_number = account_id.account_number
                channel_code = account_id.channel_code
            else:
                return False
            if seller and seller.xendit_account_id:
                key = acquirer_obj.get_encrpt_secret_key()
                unique_key = "%s-%s-%s" % (self.name, self.id, self.xendit_unique_key)
                headers = {
                    "content-type" : "application/json",
                    "XENDIT-IDEMPOTENCY-KEY": unique_key,
                    "for-user-id": seller.xendit_account_id,
                    "Authorization" : "Basic "+key
                }
                url = "https://api.xendit.co/disbursements"
                data = {
                    "reference_id": unique_key,
                    "channel_code": channel_code,
                    "account_name": account_holder_name,
                    "account_number": account_number,
                    "description": "Seller Payment Ref: %s" % self.name,
                    "currency": "PHP",
                    "amount": abs(self.payable_amount)
                }
                data = json.dumps(data)
                result = requests.post(url, data=data, headers=headers)
                result = result.json()
                if result.get('id'):
                    rec = rec.sudo()
                    rec.xendit_disbursement_id = result['id']
                    rec.xendit_account_holder_name = account_holder_name
                    rec.xendit_account_number = account_number
                    rec.xendit_channel_code = result.get('channel_code')
                    if result['status'] == "COMPLETED":
                        rec.update_success_xendit_seller_disbursement()
                    elif result['status'] == "FAILED":
                        rec.update_failed_xendit_seller_disbursement('Seller Disbursement Failed.')
                    else:
                        rec.xendit_disbursement_status = result['status']
                else:
                    error_message = "%s:-%s" % (result.get('error_code',''),result.get('message','')) if result.get('error_code') else result.get('message')
                    raise Warning(error_message)

    def get_disbursement_wizard(self):
        return {
            'name':'Seller Payment Disbursement',
            'type':'ir.actions.act_window',
            'res_model':'seller.disbursement.wizard',
            'view_mode':'form',
            'binding_view_types':'form',
            'view_id':self.env.ref('wk_marketplace_xendit.wk_seller_disbursement_wizard_form_view').id,
            'target':'new',
		}

    def retry_xendit_failed_payment(self):
        self.create_xendit_seller_disbursement(retry=True)

    def pay_manually_in_odoo(self):
        self.ensure_one()
        self.is_xendit_payment = False


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create_seller_payment_new(self, sellers_dict):
        result = super(AccountMove, self).create_seller_payment_new(sellers_dict)
        invoice_id = sellers_dict.get('invoice_id',False)
        if invoice_id:
            invoice_obj = self.browse(int(invoice_id))
            transaction_id = invoice_obj.transaction_ids.filtered(lambda transaction: transaction.state == 'done')
            transaction_id = transaction_id[0] if transaction_id else False
            if transaction_id and transaction_id.acquirer_id and transaction_id.acquirer_id.provider in ['xendit_cards','xendit_ewallets']:
                vals = {
                    'payment_type': 'dr',
                    "payment_mode": "seller_payment",
                    "state": "requested",
                    "description": sellers_dict["description"],
                    "memo": sellers_dict["memo"],
                    "acquirer_id": transaction_id.acquirer_id.id,
                    "is_xendit_payment": True,
                }
                invoice_currency = sellers_dict["invoice_currency"]
                for seller in sellers_dict["seller_ids"].keys():
                    payment_method_ids = self.env["res.partner"].browse(seller).payment_method.ids
                    if payment_method_ids:
                        payment_method = payment_method_ids[0]
                    else:
                        payment_method = False
                    vals.update({"seller_id": seller})
                    vals.update({"payment_method": payment_method})
                    total_amount = 0
                    for amount in sellers_dict["seller_ids"][seller]["invoice_line_payment"]:
                        total_amount += amount
                    mp_currency_obj = self.env["res.currency"].browse(self.env['ir.default'].get('res.config.settings', 'mp_currency_id')) or self.env.user.currency_id
                    vals['name'] = self.env['ir.sequence'].next_by_code('seller.payment') or 'NEW PAY'
                    vals.update({
                        "invoiced_amount": total_amount,
                        "payable_amount": invoice_currency.compute(total_amount, mp_currency_obj),
                        "invoice_line_ids": [(6, 0,sellers_dict["seller_ids"][seller]["invoice_line_ids"])],
                    })
                    seller_payment_id = self.env['seller.payment'].with_context(pass_create_validation=True).create(vals)
        return result
