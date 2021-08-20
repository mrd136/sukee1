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
from odoo.addons.marketplace_hyperlocal_system.controllers.main import Website
import logging
_logger = logging.getLogger(__name__)

class SellerShipArea(models.Model):
    _name = 'seller.ship.area'
    _description = "Seller Ship Area"

    @api.onchange('name')
    def _onchangeArea(self):
        apikey = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
        if not apikey:
            raise UserError(_(
                "API key for GeoCoding (Places) required.\n"
                "Visit https://developers.google.com/maps/documentation/geocoding/get-api-key for more information."
            ))
        address = self.name
        if address:
            data = Website().hyperlocal_geo_find(address,apikey)
            if data:
                self.latitude = data[0]
                self.longitude = data[1]

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    seller_id = fields.Many2one("res.partner", string="Seller", default=_set_seller_id,
        copy=False, required=True)
    name = fields.Text(string="Ship Area Address",  translate=True, copy=False)
    latitude = fields.Float(string="Latitude", copy=False)
    longitude = fields.Float(string="Longitude", copy=False)
