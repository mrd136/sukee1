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
  "name"                 :  "Website Guest Checkout",
  "summary"              :  """The module allows you to disallow guest checkout for customers. The customers would need to login to make a purchase on the Odoo website.""",
  "category"             :  "Website",
  "version"              :  "2.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-Guest-Checkout.html",
  "description"          :  """Odoo Website Guest Checkout
Restrict customers to login
Website Login
Odoo Customer account login
Stop guest checkout on Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_guest_checkout",
  "depends"              :  [
                             'website_sale',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'views/views.xml',
                             'views/res_config_settings.xml',
                             'views/website_webkul_addons.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  35,
  "currency"             :  "USD",
}