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

import logging
_logger = logging.getLogger(__name__)

import base64
import json
import requests

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'


    provider = fields.Selection(selection_add=[('xendit_cards', 'Xendit Credit/Debit Cards')])
    xendit_public_key = fields.Char("Public Key", required_if_provider='xendit_cards', help="Enter Xendit Public Key.")
    xendit_secret_key = fields.Char("Secret Key", required_if_provider='xendit_cards', help="Enter Xendit Secret Key with write permissions.")

    def get_encrpt_xendit_key(self, key):
        key = key+":"
        key = key.encode("utf-8")
        key = base64.b64encode(key)
        return key.decode("utf-8")

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

    @api.model
    def xendit_cards_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'acquirer_id': self.id,
            'partner_id': int(data['partner_id']),
            'name': data.get("masked_card_number"),
            'acquirer_ref': data.get('token_id'),
            "xendit_authentication_id": data.get("authentication_id")
        })
        return payment_token

class TxXendit(models.Model):
    _inherit = 'payment.transaction'

    def xendit_cards_s2s_do_transaction(self, **data):
        self.ensure_one()
        token = self.payment_token_id
        acquirer_obj = self.acquirer_id
        key = acquirer_obj.get_encrpt_secret_key()
        headers = {
            "content-type" : "application/json",
            "Authorization" : "Basic "+key
        }
        url = "https://api.xendit.co/credit_card_charges"
        data = {
            "token_id" : token.acquirer_ref,
            "external_id": "odoo-token-id-"+str(token.id),
            "amount": self.amount
        }
        if token.xendit_authentication_id:
            data["authentication_id"] = token.xendit_authentication_id
        data = json.dumps(data)
        result = requests.post(url, data=data, headers=headers)
        result = result.json()
        return self._xendit_cards_s2s_validate_tree(result)

    def _xendit_cards_s2s_validate_tree(self, data):
        status = data.get('status')
        if status == "CAPTURED":
            self.write({
                'acquirer_reference': data.get('id'),
            })
            self._set_transaction_done()
            return True
        elif status == "AUTHORIZED":
            self.write({
                'acquirer_reference': data.get('id'),
            })
            self._set_transaction_authorized()
            return True
        elif status == "FAILED":
            self.write({
                'acquirer_reference': data.get('id'),
            })
            self._set_transaction_error(msg=data.get('failure_reason'))
            return True
        else:
            return True

class PaymentToken(models.Model):
    _inherit = 'payment.token'

    xendit_authentication_id = fields.Char('Xendit Authentication ID')
