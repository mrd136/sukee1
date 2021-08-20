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

import logging
_logger = logging.getLogger(__name__)

class SellerDisbursementWizard(models.TransientModel):
    _name = 'seller.disbursement.wizard'
    _description = "Seller Disbursement Wizard"

    @api.model
    def default_get(self,default_fields):
        res = super(SellerDisbursementWizard,self).default_get(default_fields)
        resConfig = self.env['res.config.settings']
        payment_id = self.env['seller.payment'].browse(self._context.get('active_id'))
        res['payment_id'] = payment_id.id
        res['seller_id'] = payment_id.seller_id.id
        res['amount'] = abs(payment_id.payable_amount)
        res['currency_id'] = payment_id.currency_id.id
        return res

    payment_id = fields.Many2one("seller.payment", readonly=True)
    amount = fields.Float(string="Amount", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    seller_id = fields.Many2one("res.partner", string="Seller", readonly=True)
    seller_xendit_account_id = fields.Many2one('xendit.seller.accounts', string="Seller Xendit Account", required=True)

    def confirm_seller_disbursement(self):
        return self.payment_id.create_xendit_seller_disbursement(account_id=self.seller_xendit_account_id)
