# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import http, tools,api, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.website_sale.controllers.main import WebsiteSale, QueryURL, TableCompute
from odoo import http
from odoo.addons.odoo_marketplace.controllers.main import MarketplaceSellerShop, MarketplaceSellerProfile
from odoo import SUPERUSER_ID
import urllib.parse as urlparse
from urllib.parse import urlencode
from odoo.exceptions import UserError
import requests

import logging
_logger = logging.getLogger(__name__)

class MpHyperlocal(http.Controller):

    @http.route('/check/hyperlocal/enable', type='json', auth="none", website=True)
    def get_session_info(self):
        values = {}
        mp_config_obj = request.env["res.config.settings"].sudo().get_values()
        values["enable_hyperlocal"] = mp_config_obj.get("enable_hyperlocal")
        return values

class Website(Home):

    def hyperlocal_geo_find(self,addr, apikey=False):

        if not addr:
            return None
        if not apikey:
            raise UserError(_(
                "API key for GeoCoding (Places) required.\n"
                "Visit https://developers.google.com/maps/documentation/geocoding/get-api-key for more information."
            ))

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        try:
            result = requests.get(url, params={'sensor': 'false', 'address': addr, 'key': apikey}).json()
        except Exception as e:
            raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

        if result['status'] != 'OK':
            if result.get('error_message'):
                _logger.error(result['error_message'])
                error_msg = _('Unable to geolocate, received the error:\n%s'
                            '\n\nGoogle made this a paid feature.\n'
                            'You should first enable billing on your Google account.\n'
                            'Then, go to Developer Console, and enable the APIs:\n'
                            'Geocoding, Maps Static, Maps Javascript.\n'
                            % result['error_message'])
                raise UserError(error_msg)

        try:
            geo = result['results'][0]['geometry']['location']
            return float(geo['lat']), float(geo['lng'])
        except (KeyError, ValueError, IndexError):
            return None

    @http.route(['/get/lat/long'], type='http', auth="public", website=True)
    def get_lat_long(self, **kw):
        location = request.session.get('deflocation')
        if location:
            apikey = request.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
            data = self.hyperlocal_geo_find(location,apikey)
            if data:
                latitude = data[0]
                longitude = data[1]
                request.session['latitude'] = latitude
                request.session['longitude'] = longitude
                website_order = request.website.sale_get_order()
                if website_order:
                    website_order.sudo().unlink()
        return request.redirect("/shop")

    @http.route(['/set/temp/location'], type='json', auth="public", methods=['POST'], website=True)
    def set_temp_location(self, location="", **kw):
        request.session['deflocation'] = location
        return True

    @http.route(['/set/current/location'], type='json', auth="public", methods=['POST'], website=True)
    def set_current_location(self, location="", latitude=0.0, longitude=0.0, **kw):
        if request.session.get('defCustomerlocation'):
            return False
        else:
            request.session['defCustomerlocation'] = True
            request.session['deflocation'] = location
            request.session['latitude'] = latitude
            request.session['longitude'] = longitude
            website_order = request.website.sale_get_order()
            if website_order:
                website_order.sudo().unlink()
        return True

class WebsiteSale(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        location = False
        latitude = False
        longitude = False
        res = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            latLong = request.env['seller.ship.rate'].sudo().getdefaultLongLat()
            if latLong:
                sellerShipAreaObjs = request.env['seller.ship.area'].sudo().search([])
                sellerIds = self.getAvailableSellers(sellerShipAreaObjs, latLong)
                if sellerIds:
                    productObjs = request.env['product.template'].sudo().search([('marketplace_seller_id', 'in', sellerIds)])
                    productIds = productObjs.ids
                    res.append(('id', 'in', productIds))
                else:
                    res.append(('id', 'in', []))
        return res

    def getAvailableSellers(self, sellerShipAreaObjs, latLong):
        sellerIds = []
        defaultDistance = request.website.distance
        for sellerShipAreaObj in sellerShipAreaObjs:
            areaLatLong = [sellerShipAreaObj.latitude, sellerShipAreaObj.longitude]
            distance = request.env['seller.ship.rate'].sudo().getDistance(areaLatLong, latLong)
            if defaultDistance >= distance:
                sellerIds.append(sellerShipAreaObj.seller_id.id)
        return sellerIds

    @http.route('/shop/products/autocomplete', type='json', auth='public', website=True)
    def products_autocomplete(self, term, options={}, **kwargs):
        res = super(WebsiteSale, self).products_autocomplete(term=term, options=options, kwargs=kwargs)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            url = request.httprequest.referrer
            url_parts = list(urlparse.urlparse(url))
            location = False
            latitude = False
            longitude = False
            latLong = request.env['seller.ship.rate'].sudo().getdefaultLongLat()
            if latLong:
                sellerShipAreaObjs = request.env['seller.ship.area'].sudo().search([])
                sellerIds = WebsiteSale().getAvailableSellers(sellerShipAreaObjs, latLong)

            if url_parts and url_parts[2] and '/seller/shop/' in url_parts[2]:
                url_handler = url_parts[2].split("/seller/shop/",1)[1]
                shop = request.env['seller.shop'].sudo().search([('url_handler','=',url_handler)], limit=1)
                seller_id = shop.seller_id and shop.seller_id.id

                if not seller_id in sellerIds:
                    prod_list = []
                    res.update({'products' : prod_list, 'products_count': len(prod_list)})

        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        res = super(WebsiteSale, self).checkout_form_validate(mode, all_form_values, data)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            customerLatLong = self.getCustomerLocation(data)
            if customerLatLong:
                latLong = request.env['seller.ship.rate'].sudo().getdefaultLongLat()
                if latLong:
                    distance = request.env['seller.ship.rate'].sudo().getDistance(latLong, customerLatLong)
                    defaultDistance = request.website.distance
                    if distance > defaultDistance:
                        res[0]["country_id"] = 'error'
                        res[0]["state_id"] = 'error'
                        res[1].append(_('Sorry! Shipping address should belong to the selected location.'))
            else:
                res[0]["country_id"] = 'error'
                res[0]["state_id"] = 'error'
                res[1].append(_('Sorry! Shipping address should belong to the selected location.'))
        return res

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        res = super(WebsiteSale, self).checkout(**post)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            if request.session.get('shippings'):
                request.session['shippings'] = False
                return request.redirect('/shop/address')
        return res

    def checkout_values(self, **kw):
        order = request.website.sale_get_order()
        res = super(WebsiteSale, self).checkout_values(**kw)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            shippingIds = []
            if res.get('shippings'):
                shippingObjs = res.get('shippings')
                latLong = request.env['seller.ship.rate'].sudo().getdefaultLongLat()
                if latLong:
                    defaultDistance = request.website.distance
                    for shippingObj in shippingObjs:
                        shippingObj.geo_localize()
                        if shippingObj.partner_latitude:
                            customerLatLong = [shippingObj.partner_latitude, shippingObj.partner_longitude]
                            distance = request.env['seller.ship.rate'].sudo().getDistance(latLong, customerLatLong)
                            if distance <= defaultDistance:
                                shippingIds.append(shippingObj)
                res['shippings'] = shippingIds
                if not shippingIds:
                    request.session['shippings'] = 'address'
        return res

    def getCustomerLocation(self, data):
        street = data.get('street') or ''
        city = data.get('city') or ''
        zip = data.get('zip') or ''
        countryId = data.get('country_id')
        stateName = ''
        countryName = ''
        if countryId:
            countryObj = request.env['res.country'].search([('id', '=', countryId)])
            countryName = countryObj.name
        stateId = data.get('state_id')
        if stateId:
            stateObj = request.env['res.country.state'].search([('id', '=', stateId)])
            stateName = stateObj.name
        address = request.env['base.geocoder'].sudo().geo_query_address(street=street,
                                            zip=zip,
                                            city=city,
                                            state=stateName,
                                            country=countryName)

        result = request.env['base.geocoder'].sudo().geo_find(address, force_country=countryName)
        if result is None:
            address = request.env['base.geocoder'].sudo().geo_query_address(city=city,
                                                state=stateName,
                                                country=countryName)
            result = request.env['base.geocoder'].sudo().geo_find(address, force_country=countryName)
        return result

class MarketplaceSellerShop(MarketplaceSellerShop):

    def checkhyperlocal(self,seller_id):
        location = False
        latitude = False
        longitude = False
        latLong = request.env['seller.ship.rate'].sudo().getdefaultLongLat()
        if latLong:
            sellerShipAreaObjs = request.env['seller.ship.area'].sudo().search([])
            sellerIds = WebsiteSale().getAvailableSellers(sellerShipAreaObjs, latLong)
            if seller_id in sellerIds:
                productObjs = request.env['product.template'].sudo().search([('marketplace_seller_id', 'in', [seller_id])])
                productIds = productObjs.ids
                hyperlocaldomain = ('id', 'in', productIds)
            else:
                hyperlocaldomain = ('id', 'in', [])
            return hyperlocaldomain

    @http.route(['/seller/shop/<shop_url_handler>', '/seller/shop/<shop_url_handler>/page/<int:page>'], type='http', auth="public", website=True)
    def seller_shop(self, shop_url_handler, page=0, category=None, search='', ppg=False, **post):
        response = super(MarketplaceSellerShop,self).seller_shop(shop_url_handler, page, category, search, ppg, **post)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            seller = response.qcontext.get("shop_obj").seller_id
            if seller:
                seller_id = seller.id
                hyperlocaldomain = MarketplaceSellerShop().checkhyperlocal(seller_id)
                if not hyperlocaldomain:
                    hyperlocaldomain = ("marketplace_seller_id", "=", seller.id)
                pager = response.qcontext.get("pager")
                PPR = response.qcontext.get("ppr")
                ppg = response.qcontext.get("ppg")

                def _get_search_domain(search):
                    domain = request.website.sale_product_domain()
                    domain += [hyperlocaldomain]
                    if search:
                        for srch in search.split(" "):
                            domain += [
                                '|', '|', '|', ('name', 'ilike',
                                                srch), ('description', 'ilike', srch),
                                ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

                    product_obj = request.env['product.template'].sudo().search(domain)
                    return request.env['product.template'].browse(product_obj.ids)

                product_count = request.env["product.template"].sudo().search_count([('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True),hyperlocaldomain])
                products = request.env['product.template'].sudo().search([('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True), hyperlocaldomain], limit=ppg, offset=pager['offset'], order='website_published desc, website_sequence desc')

                response.qcontext.update({
                "product_count": product_count,
                'products': products,
                'bins': TableCompute().process(products if not search else _get_search_domain(search), ppg, PPR),
                })
        return response

    @http.route('/seller/shop/recently-product/', type='json', auth="public", website=True)
    def seller_shop_recently_product(self, shop_id, page=0, category=None, search='', ppg=False, **post):

        uid, context, env = request.uid, dict(request.env.context), request.env
        url = "/seller/shop/" + str(shop_id)
        shop_obj = env["seller.shop"].sudo().browse(shop_id)
        recently_product = request.website.mp_recently_product

        page = 0
        category = None
        search = ''
        ppg = False

        enable_hyperlocal = request.website.enable_hyperlocal


        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg

        PPR = request.env['website'].get_current_website().shop_ppr
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if not context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = env['product.pricelist'].sudo().browse(context['pricelist'])

        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list)

        recently_product_obj = request.env['product.template'].search([('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True), (
            "marketplace_seller_id", "=", shop_obj.seller_id.id)], order='create_date desc, website_published desc, website_sequence desc', limit=recently_product)
        product_count = len(recently_product_obj.ids)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=20, scope=7, url_args=post)
        if enable_hyperlocal:
            seller = shop_obj.seller_id
            seller_id = seller.id
            hyperlocaldomain = MarketplaceSellerShop().checkhyperlocal(seller_id)
            if not hyperlocaldomain:
                hyperlocaldomain = [("id", "in", recently_product_obj.ids)]
            else:
                hyperlocaldomain = [hyperlocaldomain,("id", "in", recently_product_obj.ids)]

        product_ids = request.env['product.template'].search(hyperlocaldomain, limit=ppg, offset=pager[
                                                             'offset'], order='website_published desc, website_sequence desc')
        products = env['product.template'].browse(product_ids.ids)

        from_currency = env['res.users'].sudo().browse(uid).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: env['res.currency'].sudo()._compute(from_currency, to_currency, price)

        values = {
            'rows': PPR,
            'bins': TableCompute().process(products, ppg, PPR),
            'ppg': ppg,
            'ppr': PPR,
            'pager': pager,
            'products': products,
            "keep": keep,
            'compute_currency': compute_currency,
            "pricelist": pricelist,
            'shop_obj': shop_obj,
        }
        return request.env.ref('odoo_marketplace.shop_recently_product').render(values, engine='ir.qweb')

class MarketplaceSellerProfile(MarketplaceSellerProfile):

    @http.route(['/seller/profile/<int:seller_id>',
        '/seller/profile/<int:seller_id>/page/<int:page>',
        '/seller/profile/<seller_url_handler>',
        '/seller/profile/<seller_url_handler>/page/<int:page>'],
        type='http', auth="public", website=True)
    def seller(self, seller_id=None, seller_url_handler=None, page=0, category=None, search='', ppg=False, **post):
        response = super(MarketplaceSellerProfile,self).seller(seller_id, seller_url_handler, page, category, search, ppg, **post)
        enable_hyperlocal = request.website.enable_hyperlocal
        if enable_hyperlocal:
            seller = response.qcontext.get("seller")
            if seller:
                seller_id = seller.id
                pager = response.qcontext.get("pager")
                PPR = response.qcontext.get("ppr")
                ppg = response.qcontext.get("ppg")

                hyperlocaldomain = MarketplaceSellerShop().checkhyperlocal(seller_id)
                if not hyperlocaldomain:
                    hyperlocaldomain = ("marketplace_seller_id", "=", seller.id)

                seller_product_ids = request.env["product.template"].search([("marketplace_seller_id", "=", seller.id)])
                product_count = request.env["product.template"].sudo().search_count([('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True), ("id", "in", seller_product_ids.ids),hyperlocaldomain])
                products = request.env['product.template'].sudo().search([('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True), hyperlocaldomain], limit=ppg, offset=pager['offset'], order='website_published desc, website_sequence desc')

                response.qcontext.update({
                    "product_count": product_count,
                    'products': products,
                    'bins': TableCompute().process(products, ppg, PPR),
                })
        return response

    @http.route('/seller/profile/recently-product/', type='json', auth="public", website=True)
    def seller_profile_recently_product(self, seller_id, page=0, category=None, search='', ppg=False, **post):
        enable_hyperlocal = request.website.enable_hyperlocal

        if not seller_id:
            return False
        uid, context, env = request.uid, dict(request.env.context), request.env
        url = "/seller/" + str(seller_id)
        seller_obj = env["res.partner"].sudo().browse(seller_id)
        recently_product = request.website.mp_recently_product

        page = 0
        category = None
        search = ''
        ppg = False

        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg

        PPR = request.env['website'].get_current_website().shop_ppr
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if not context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = env['product.pricelist'].sudo().browse(context['pricelist'])

        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/profile/', category=category and int(category),
                        search=search, attrib=attrib_list)
        recently_product_obj = request.env['product.template'].search([
                ('sale_ok', '=', True),
                ('status', '=', "approved"),
                ("website_published", "=", True),
                ("marketplace_seller_id", "=", seller_obj.id)
            ],
            order='create_date desc, website_published desc, website_sequence desc',
            limit=recently_product
        )
        product_count = len(recently_product_obj.ids)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=20, scope=7, url_args=post)

        if enable_hyperlocal:
            seller_id = seller_obj.id
            hyperlocaldomain = MarketplaceSellerShop().checkhyperlocal(seller_id)
        if not hyperlocaldomain:
            hyperlocaldomain = [("id", "in", recently_product_obj.ids)]
        else:
            hyperlocaldomain = [hyperlocaldomain,("id", "in", recently_product_obj.ids)]

        product_ids = request.env['product.template'].search(hyperlocaldomain, limit=ppg, offset=pager[
                                                             'offset'], order='website_published desc, website_sequence desc')
        products = env['product.template'].browse(product_ids.ids)
        from_currency = env['res.users'].sudo().browse(uid).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: env['res.currency'].sudo()._compute(from_currency, to_currency, price)

        values = {
            'rows': PPR,
            'bins': TableCompute().process(products, ppg, PPR),
            'ppg': ppg,
            'ppr': PPR,
            'pager': pager,
            'products': products,
            "keep": keep,
            'compute_currency': compute_currency,
            "pricelist": pricelist,
            'seller_obj': seller_obj,
        }
        return request.env.ref('odoo_marketplace.shop_recently_product').render(values, engine='ir.qweb')
