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

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add = [('hyperlocal_shipping','Hyperlocal Shipping')])
    hyperlocal_default_price = fields.Float('Default Price')

    def hyperlocal_shipping_get_shipping_price_from_so(self, orders):
        price = self.hyperlocal_shipping_shipping_rate(orders)
        return price

    def hyperlocal_shipping_rate_shipment(self, order):
        try:
            res = {}
            price = 0.0
            latLong = self.env['seller.ship.rate'].sudo().getdefaultLongLat()
            if order:
                if latLong:
                    customerShippingObj = order.partner_shipping_id
                    customerLatLong = self.getCustomerLocation(customerShippingObj)
                    if customerLatLong:
                        distance = self.env['seller.ship.rate'].sudo().getDistance(latLong, customerLatLong)
                        price = self.getShippingRate(order, distance)
            res['price'] = price
            res['error_message'] = False
            res['warning_message'] = False
            res['success'] = True
            return res
        except Exception as e:
            res['price'] = price
            res['error_message'] = e
            res['success'] = False
            res['warning_message'] = False
            return res

    def getCustomerLocation(self, customerShippingObj):
        street = customerShippingObj.street or ''
        zip = customerShippingObj.zip or ''
        city = customerShippingObj.city or ''
        state = customerShippingObj.state_id.name or ''
        country = customerShippingObj.country_id.name or ''
        address = self.env['base.geocoder'].sudo().geo_query_address(street=street,
                                            zip=zip,
                                            city=city,
                                            state=state,
                                            country=country)
        apiKey = request.website.sudo().google_maps_api_key
        result = self.env['base.geocoder'].sudo().geo_find(address)
        if result is None:
            address = request.env['base.geocoder'].sudo().geo_query_address(city=city,
                                                state=state,
                                                country=country)
            result = request.env['base.geocoder'].sudo().geo_find(address, force_country=countryName)
        return result

    def getShippingRate(self, order, actualDistance):
        orderLineObjs = order.order_line
        shipping_cost_type = self.env['res.config.settings'].get_mp_global_field_value('shipping_cost_type')
        carrierRate = order.carrier_id.hyperlocal_default_price
        if not shipping_cost_type == "seller_wise":
            shippingRate = 0.0
            for orderLineObj in orderLineObjs:
                productWeight = orderLineObj.product_id.weight
                sellerObj = orderLineObj.product_id.marketplace_seller_id
                if sellerObj:
                    sellerShipRateObj = self.env['seller.ship.rate'].sudo().search([('distance_from', '<=', actualDistance), ('distance_to', '>=', actualDistance), ('weight_from', '<=', productWeight), ('weight_to', '>=', productWeight), ('name', '=', sellerObj.id)],limit=1)
                    if sellerShipRateObj:
                        sellerPrice = sellerShipRateObj.cost
                        shippingRate = shippingRate + sellerPrice
                    else:
                        shippingRate = shippingRate + carrierRate
            return shippingRate
        else:
            seller_wise_products = {}
            for orderLineObj in orderLineObjs:
                product_id = orderLineObj.product_id
                sellerObj = orderLineObj.product_id.marketplace_seller_id
                if sellerObj in seller_wise_products.keys() and sellerObj:
                    seller_wise_products[sellerObj].append(product_id)
                elif  sellerObj:
                    seller_wise_products[sellerObj] = [product_id]

            final_shipping_rate = 0.0
            for seller_id,product_ids in seller_wise_products.items():
                shippingRate = 0.0
                sellerShipRateObjlist = []
                for product_id in product_ids:
                    productWeight = product_id.weight
                    sellerObj = seller_id
                    sellerShipRateObj = self.env['seller.ship.rate'].sudo().search([('distance_from', '<=', actualDistance), ('distance_to', '>=', actualDistance), ('weight_from', '<=', productWeight), ('weight_to', '>=', productWeight), ('name', '=', sellerObj.id)],limit=1)
                    if sellerShipRateObj:
                        if sellerShipRateObj.id not in sellerShipRateObjlist:
                            sellerPrice = sellerShipRateObj.cost
                            price = shippingRate + sellerPrice
                            shippingRate = shippingRate + sellerPrice
                            sellerShipRateObjlist.append(sellerShipRateObj.id)
                    else:
                        shippingRate = shippingRate + carrierRate
                final_shipping_rate = final_shipping_rate + shippingRate

            return final_shipping_rate

    def hyperlocal_shipping_send_shipping(self, pickings):
        res = []
        for p in pickings:
            res = res + [{'exact_price': p.carrier_id.hyperlocal_default_price,
                          'tracking_number': False}]
        return res
