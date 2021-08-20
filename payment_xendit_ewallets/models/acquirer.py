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
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare
from werkzeug import urls

import logging
_logger = logging.getLogger(__name__)

import base64
import json
import requests

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('xendit_ewallets', 'Xendit eWallets')])
    xendit_wallet_type = fields.Selection([('PH_PAYMAYA','Paymaya'),('PH_GCASH','GCash'),('PH_GRABPAY','Grabpay')], string="eWallet Type")
    xendit_public_key = fields.Char("Public Key", required_if_provider='xendit_ewallets', help="Enter Xendit Public Key.")
    xendit_secret_key = fields.Char("Secret Key", required_if_provider='xendit_ewallets', help="Enter Xendit Secret Key with write permissions.")

    def get_encrpt_public_key(self):
        if not self.xendit_public_key:
            raise ValidationError(_("No public key found! Please configure a public key."))
        else:
            key = self.xendit_public_key+":"
            key = key.encode("utf-8")
            key = base64.b64encode(key)
            return key.decode("utf-8")

    def get_encrpt_secret_key(self):
        if not self.xendit_secret_key:
            raise ValidationError(_("No secret key found! Please configure a secret key."))
        else:
            key = self.xendit_secret_key+":"
            key = key.encode("utf-8")
            key = base64.b64encode(key)
            return key.decode("utf-8")

    def get_xendit_ewallet_url(self, values):
        self.ensure_one()
        base_url = self.get_base_url()
        key = self.get_encrpt_secret_key()
        headers = {
            "content-type" : "application/json",
            "Authorization" : "Basic "+key
        }
        url = "https://api.xendit.co/ewallets/charges"
        data = {
            "reference_id" : values.get('reference'),
            "currency": "PHP",
            "amount": values.get('amount'),
            "checkout_method":"ONE_TIME_PAYMENT",
            "channel_code":self.xendit_wallet_type,
            "channel_properties":{
                "success_redirect_url":urls.url_join(base_url, "/xendit/eWallet/success"),
                "failure_redirect_url":urls.url_join(base_url, "/xendit/eWallet/error"),
            },
        }
        if self.xendit_wallet_type == 'PH_PAYMAYA':
            data["channel_properties"].update({
                "cancel_redirect_url": urls.url_join(base_url, "/xendit/eWallet/cancel"),
            })
        data = json.dumps(data)
        result = requests.post(url, data=data, headers=headers)
        result = result.json()
        if result.get('error_code'):
            return {
                "xendit_error_msg": result.get('message'),
                "xendit_redirect_url": False
            }
        if result.get('actions'):
            actions = result['actions']
            return {
                "xendit_error_msg": False,
                "xendit_redirect_url": actions.get('desktop_web_checkout_url', False)
            }
        return {
            "xendit_error_msg": "Something went wrong with the eWallet api's.",
            "xendit_redirect_url": False
        }

    def xendit_ewallets_form_generate_values(self, values):
        tx_values = dict(values)
        actions = self.get_xendit_ewallet_url(values)
        tx_values.update({
            "xendit_wallet_type": self.xendit_wallet_type,
        })
        tx_values.update(actions)
        return tx_values

class TxXendit(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _xendit_ewallets_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        if not reference:
            error_msg = _('Xendit: received data with missing reference.')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Paypal: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _xendit_ewallets_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _xendit_ewallets_form_validate(self, data):
        status = data.get('status')
        if status == "SUCCEEDED":
            self.write({
                'acquirer_reference': data.get('charge_id'),
            })
            self._set_transaction_done()
            return True
        elif status in ["PENDING", "VOIDED"]:
            self.write({
                'acquirer_reference': data.get('charge_id'),
            })
            self._set_transaction_pending()
            return True
        elif status == "FAILED":
            self.write({
                'acquirer_reference': data.get('charge_id'),
            })
            self._set_transaction_error(msg=data.get('failure_reason'))
            return True
        else:
            return True
