# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models, _
from odoo.http import request

class GeoIPRedirectSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'website.guest.checkout'
    
    enable_guest = fields.Boolean(string='Enable Guest Checkout',related='website_id.enable_guest',readonly=False)