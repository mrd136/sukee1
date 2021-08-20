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
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing

import logging
_logger = logging.getLogger(__name__)

class XenditCards(http.Controller):

    @http.route(['/xendit/cards/create/token',], type='json', auth="public", methods=['POST'], website=True)
    def xendit_cards_create_token(self, **post):
        order = request.website.sale_get_order()
        if not order:
            return '/shop/?error=no_order'
        else:
            acquirer_obj = request.env['payment.acquirer'].search([('provider','=','xendit_cards')], limit=1)
            data = {
                "token_id" : post.get('id'),
                "masked_card_number": post.get('masked_card_number'),
                "partner_id": order.partner_id.id,
                "amount": order.amount_total
            }
            if post.get('authentication_id'):
                data["authentication_id"] = post.get('authentication_id')
            token = acquirer_obj.s2s_process(data)

            assert order.partner_id.id != request.website.partner_id.id

            vals = {'payment_token_id': token.id, 'return_url': '/shop/payment/validate'}

            tx = order._create_payment_transaction(vals)
            PaymentProcessing.add_payment_transaction(tx)
            return "/payment/process"
