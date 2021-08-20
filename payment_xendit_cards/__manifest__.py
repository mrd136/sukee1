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
  "name"                 :  "Website Xendit Cards Payment Acquirer",
  "summary"              :  """Website Xendit Cards Payment Acquirer""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """Website Xendit Cards Payment Acquirer""",
  "depends"              :  ['payment'],
  "data"                 :  [
                                'views/xendit_templates.xml',
                                'views/acquirer_views.xml',
                                'data/xendit_cards_demo.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  69,
  "currency"             :  "USD",
  "post_init_hook"       :  "create_missing_journal_for_acquirers",
  # "uninstall_hook"       :  "uninstall_hook",
  "pre_init_hook"        :  "pre_init_check",
}
