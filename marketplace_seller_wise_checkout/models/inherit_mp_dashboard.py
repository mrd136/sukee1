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

class marketplace_dashboard(models.Model):
    _inherit = "marketplace.dashboard"

    def _get_approved_count(self):
        res = super(marketplace_dashboard, self)._get_approved_count()
        for rec in self:
            if rec.state == 'order':
                if rec.is_seller:
                    user_obj = self.env['res.users'].browse(self._uid)
                    obj = self.env['sale.order'].search(
                        [('marketplace_seller_id', '=',user_obj.partner_id.id), ('mp_order_state', '=', 'approved')])
                else:
                    obj = self.env['sale.order'].search(
                        [('marketplace_seller_id', '!=', False), ('mp_order_state', '=', 'approved')])
                rec.count_product_approved = len(obj)
        return res

    def _get_pending_count(self):
        res = super(marketplace_dashboard, self)._get_pending_count()
        for rec in self:
            if rec.state == 'order':
                user_obj = rec.env['res.users'].browse(self._uid)
                if rec.is_seller:
                    obj = rec.env['sale.order'].search(
                        [('marketplace_seller_id', '=',user_obj.partner_id.id), ('mp_order_state', '=', 'new')])
                else:
                    obj = rec.env['sale.order'].search(
                        [('marketplace_seller_id', '!=', False), ('mp_order_state', '=', 'new')])
                rec.count_product_pending = len(obj)
        return res
