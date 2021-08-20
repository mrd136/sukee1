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

from odoo import api, models, fields, _
import logging
import random
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", domain="[('seller','=',True)]", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'],)

    mp_order_state = fields.Selection([
        ("new","New"),
        ("approved","Approved") ,
        ("shipped","Shipped"),
        ("cancel","Cancelled")], default="new", copy=False)

    def button_seller_approve_order(self):
        for rec in self:
            if rec.marketplace_seller_id:
                rec.sudo().action_confirm()
                rec.sudo().write({'mp_order_state':'approved'})
                if rec.order_line:
                    for line in rec.order_line:
                        line.sudo().marketplace_state = "approved"

    def button_seller_cancel_order(self):
        for rec in self:
            if rec.marketplace_seller_id:
                rec.sudo().action_cancel()
                rec.sudo().write({'mp_order_state':'cancel'})
                if rec.order_line:
                    for line in rec.order_line:
                        line.sudo().button_cancel()

    def action_cancel(self):
        res = super(SaleOrder,self).action_cancel()
        for rec in self:
            if rec.marketplace_seller_id:
                rec.write({'mp_order_state':'cancel'})
        return res

    def action_draft(self):
        result = super(SaleOrder,self).action_draft()
        for rec in self:
            if rec.marketplace_seller_id:
                rec.write({'mp_order_state':'new'})
        return result

    def action_view_delivery(self):
        res = super(SaleOrder, self).action_view_delivery()
        if self._context.get('mp_order'):
            action = self.env.ref('odoo_marketplace.marketplace_stock_picking_action').read()[0]
            pickings = self.mapped('picking_ids')
            if len(pickings) > 1:
                action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                action['views'] = [(self.env.ref('odoo_marketplace.marketplace_picking_stock_modified_form_view').id, 'form')]
                action['res_id'] = pickings.id
            return action
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def write(self, values):
        result = super(SaleOrderLine, self).write(values)
        for rec in self:
            order = rec.order_id
            if order and all([ol.marketplace_state == 'shipped' for ol in order.order_line]):
                order.write({'mp_order_state': 'shipped'})
        return result