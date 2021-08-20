# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo Marketplace Hyperlocal System",
  "summary"              :  """The module allows the customer to locate their local sellers on the Odoo marketplace and buy products online from them. The sellers can add their address and they show up to the customers.""",
  "category"             :  "Website",
  "version"              :  "1.4.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Hyperlocal-System.html",
  "description"          :  """Odoo Marketplace Hyperlocal System
Website local sellers
Marketplace local seller
Near by seller
Near me seller
Seller near me
Website Nearest seller
Seller locale
Hyperlocal delivery
Customer location
Website Seller location
Online Local products
Geo radius
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
Multi-seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_hyperlocal_system&custom_url=/shop",
  "depends"              :  [
                             'base_geolocalize',
                             'website_sale_delivery',
                             'odoo_marketplace',
                            ],
  "data"                 :  [
                             'security/marketplace_security.xml',
                             'security/ir.model.access.csv',
                             'views/seller_ship_area_view.xml',
                             'views/website_config_view.xml',
                             'views/seller_ship_rate_view.xml',
                             'views/mp_hyperlocal_menu_view.xml',
                             'views/res_config_view.xml',
                             'views/website_templates.xml',
                             'views/delivery_carrier_view.xml',
                             'data/data_hyperlocal.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
