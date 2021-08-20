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

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_hyperlocal = fields.Boolean(string="Enable", related="website_id.enable_hyperlocal", readonly=False)
    distance = fields.Float("Distance", related="website_id.distance", readonly=False)
    def_address = fields.Char("Set Default Address", related="website_id.def_address", readonly=False)
    latitude = fields.Float(string="Latitude", related="website_id.latitude", readonly=False)
    longitude = fields.Float(string="Longitude", related="website_id.longitude", readonly=False)
    delivery_method = fields.Many2one('delivery.carrier', string="Delivery Methods",
                                     help="""Delivery Method use in customer checkout.""")
    radius_unit = fields.Selection([('km', 'Kilometer'), ('mile', 'Mile')], string="Radius Unit")
    shipping_cost_type = fields.Selection([('product_wise','Product Wise'),('seller_wise','Seller Wise')], string="Shipping Cost Type")

    @api.onchange("def_address")
    def upd_latlong(self):
        def_address = self.def_address
        if def_address:
            data = self.env['base.geocoder'].sudo().geo_find(def_address)
            if data:
                self.latitude = data[0]
                self.longitude = data[1]

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_hyperlocal', self.enable_hyperlocal)
        self.env['ir.default'].sudo().set('res.config.settings', 'distance', self.distance)
        self.env['ir.default'].sudo().set('res.config.settings', 'def_address', self.def_address or '')
        self.env['ir.default'].sudo().set('res.config.settings', 'latitude', self.latitude)
        self.env['ir.default'].sudo().set('res.config.settings', 'longitude', self.longitude)
        self.env['ir.default'].sudo().set('res.config.settings', 'delivery_method', self.delivery_method.id or False)
        self.env['ir.default'].sudo().set('res.config.settings', 'radius_unit', self.radius_unit)
        self.env['ir.default'].sudo().set('res.config.settings', 'shipping_cost_type', self.shipping_cost_type)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update({
            'enable_hyperlocal':IrDefault.get('res.config.settings','enable_hyperlocal') or self.enable_hyperlocal,
            'def_address':IrDefault.get('res.config.settings','def_address') or self.def_address or '',
            'delivery_method':IrDefault.get('res.config.settings','delivery_method') or self.delivery_method or False,
            'radius_unit':IrDefault.get('res.config.settings','radius_unit') or self.radius_unit,
            'shipping_cost_type':IrDefault.get('res.config.settings','shipping_cost_type') or self.shipping_cost_type,
        })
        return res
