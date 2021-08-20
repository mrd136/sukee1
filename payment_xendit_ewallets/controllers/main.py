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

import odoo
from odoo import http, _
from odoo.http import request, Response
import logging
_logger = logging.getLogger(__name__)

import pprint
import json

class XenditEwallet(http.Controller):

    @http.route(['/xendit/eWallet/callback'], type='json', auth='public', csrf=False, methods=['POST'], website=True)
    def xendit_eWallet_callback(self, **post):
        if request.httprequest.data:
            res_data = json.loads(request.httprequest.data)
            _logger.info('Xendit eWallet: entering form_feedback with post data %s', pprint.pformat(res_data))
            data = res_data.get('data', {})
            tx_data = {
                "charge_id": data.get('id'),
                "reference": data.get('reference_id'),
                "status": data.get('status'),
                "failure_reason": "",
                "currency": data.get('currency'),
                "amount": data.get('charge_amount'),
                "xendit_wallet_type": data.get('channel_code'),
            }
            request.env['payment.transaction'].sudo().form_feedback(tx_data, 'xendit_ewallets')
        return Response('success', status=200)

    @http.route(['/xendit/eWallet/cancel'], type='http', auth="public", methods=['GET'], website=True)
    def xendit_eWallet_cancel(self, **post):
        # _logger.info("~~~~~~~~xendit_eWallet_cancel~~~~~~~~~~~~%r~~~~~",post)
        return request.redirect('/payment/process')

    @http.route(['/xendit/eWallet/success'], type='http', auth="public", methods=['GET'], website=True)
    def xendit_eWallet_success(self, **post):
        # _logger.info("~~~~~~~~xendit_eWallet_success~~~~~~~~~~~~%r~~~~~",post)
        return request.redirect('/payment/process')

    @http.route(['/xendit/eWallet/error'], type='http', auth="public", methods=['GET'], website=True)
    def xendit_eWallet_error(self, **post):
        # _logger.info("~~~~~~~~xendit_eWallet_error~~~~~~~~~~~~%r~~~~~",post)
        return request.redirect('/payment/process')
