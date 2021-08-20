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

class XenditSellerAccount(http.Controller):

    @http.route(['/xendit/disbursement/callback'], type='json', auth='public', csrf=False, methods=['POST'], website=True)
    def xendit_disbursement_callback(self, **post):
        if request.httprequest.data:
            data = json.loads(request.httprequest.data)
            _logger.info('Xendit Disbursement Callback Data: %s', pprint.pformat(data))
            disbursement_id = data.get('id')
            if disbursement_id:
                amount = data.get('amount')
                disbursement_status = data.get('status')
            payment_id = request.env['seller.payment'].sudo().search([('xendit_disbursement_id','=',disbursement_id)],limit=1)
            if payment_id and payment_id.xendit_disbursement_status != disbursement_status:
                if disbursement_status == "COMPLETED":
                    payment_id.update_success_xendit_seller_disbursement()
                elif disbursement_status == "FAILED":
                    error_message = data.get('failure_code','Seller Disbursement Failed.')
                    payment_id.update_failed_xendit_seller_disbursement(error_message)
        return Response('success', status=200)

    @http.route(['/xendit/owned/account/callback'], type='json', auth='public', csrf=False, methods=['POST'], website=True)
    def xendit_owned_account_callback(self, **post):
        if request.httprequest.data:
            res_data = json.loads(request.httprequest.data)
            _logger.info('Xendit Owned Account Callback Data: %s', pprint.pformat(res_data))
            data = res_data.get('data', {})
            account_id = data.get('id')
            account_status = data.get('status')
            if account_id and account_status:
                seller_id = request.env['res.partner'].sudo().search([('seller','=',True),('xendit_account_id','=',account_id)],limit=1)
                if seller_id and seller_id.xendit_account_status != account_status:
                    seller_id.xendit_account_status = account_status
        return Response('success', status=200)
