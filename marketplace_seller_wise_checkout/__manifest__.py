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
  "name"                 :  "Odoo Marketplace Seller Wise Checkout",
  "summary"              :  """The module allows the customer to split the order seller wise.  The products are divided at the checkout according the respective sellers and the customer can now pay for each seller separately.""",
  "category"             :  "Website",
  "version"              :  "1.2.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Seller-Wise-Checkout.html",
  "description"          :  """Odoo Marketplace Seller Wise Checkout
Split order
Seller wise order
Seller payment
Separate seller payment
Marketplace Divide seller payment
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_seller_wise_checkout&lifetime=120&lout=1&custom_url=/",
  "depends"              :  ['odoo_marketplace'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/inherit_sale_views.xml',
                             'views/mp_so_view.xml',
                             'views/website_cart_template.xml',
                             'views/templates.xml',
                             'views/inherit_mp_dashboard_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  100.0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}