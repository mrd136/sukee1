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
from odoo.http import request
import math

class SellerShipRate(models.Model):
    _name = 'seller.ship.rate'
    _description = "Seller Ship Rate"


    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    name = fields.Many2one("res.partner", string="Seller", default=_set_seller_id,
        copy=False, required=True)
    distance_from = fields.Float("Distance From")
    distance_to = fields.Float("Distance To")
    weight_from = fields.Float("Weight From")
    weight_to = fields.Float("Weight To")
    cost = fields.Float("Shipping Cost")

    def getDistance(self, location, customerLocation):
        lat, lon = location
        cusLat, cusLon = customerLocation
        radius = 6371
        marginlat = math.radians(cusLat-lat)
        marginlon = math.radians(cusLon-lon)
        margin = math.sin(marginlat/2) * math.sin(marginlat/2) + math.cos(math.radians(lat)) \
            * math.cos(math.radians(cusLat)) * math.sin(marginlon/2) * math.sin(marginlon/2)
        circle = 2 * math.atan2(math.sqrt(margin), math.sqrt(1-margin))
        distance = radius * circle
        radiusUnit = self.env['ir.default'].sudo().get('res.config.settings', 'radius_unit')
        if radiusUnit == 'mile':
            distance = distance / 0.62137119
        return distance

    def getdefaultLongLat(self):
        latitude = request.session.get('latitude')
        longitude = request.session.get('longitude')
        if not latitude:
            latitude = self.env['ir.default'].sudo().get('res.config.settings', 'latitude')
            longitude = self.env['ir.default'].sudo().get('res.config.settings', 'longitude')
            request.session['latitude'] = latitude
            request.session['longitude'] = longitude
            website_order = request.website.sale_get_order()
            if website_order:
                website_order.sudo().unlink()
        if latitude == 0.0 and longitude == 0.0:
            default_address = self.env['ir.default'].sudo().get('res.config.settings', 'def_address')
            if default_address:
                apiKey = request.website.sudo().google_maps_api_key
                data = request.env['base.geocoder'].sudo().geo_find(default_address)
                if data:
                    latitude = data[0]
                    longitude = data[1]
                    request.session['latitude'] = latitude
                    request.session['longitude'] = longitude
                    website_order = request.website.sale_get_order()
                    if website_order:
                        website_order.sudo().unlink()
            else:
                return []
        return [latitude, longitude]
