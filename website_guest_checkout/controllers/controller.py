# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
import re

import odoo
from odoo import http, SUPERUSER_ID, _
from odoo.http import route, request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.addons.website_sale.controllers.main import WebsiteSale
_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        if request.website.is_public_user() and request.website.sudo().enable_guest:
        	return request.redirect('/web/login')
        res = super(WebsiteSale, self).payment(post=post)
        return res


class website_guest_checkout(http.Controller):

    @http.route('/checkout/login/', type='json', auth='public', website=True)
    def wk_login(self, *args, **kwargs):
        values = request.params.copy()
        values.update({'message': '', 'status': True})
        try:
            db = request.session.db
            if not db:
                values['message'] = _("No Database Selected")
                values['status'] = False
            if not request.uid:
                request.uid = SUPERUSER_ID

            if ((not kwargs.get('redirect')) or (kwargs.get('redirect') and not kwargs['redirect'])):
                kwargs['redirect'] = "/shop"
            values['redirect'] = kwargs['redirect']
            old_uid = request.uid
            uid = request.session.authenticate(
                db, values['login'], values['password'])
            values['uid'] = uid
            values['message'] = _("successfully login")
            if not uid:
                values['message'] = _("Wrong login/password")
                values['status'] = False
        except UserError as e:
            values['message'] = _("Wrong login/password")
            values['status'] = False
        except odoo.exceptions.AccessDenied as e:
            _logger.info("-----AccessDenied------ : %r", values)
            values['message'] = _("Wrong login/password")
            values['status'] = False
            values['uid'] = False
        return values

    @http.route('/checkout/signup', type='json', auth="public", website=True)
    def wk_signup(self, *args, **kw):
        res = {}
        qcontext = request.params.copy()
        try:
            values = dict((key, qcontext.get(key)) for key in (
                'login', 'name', 'password', 'confirm_password'))
            self.custom_validate(values)
            values.pop('confirm_password')
            token = ""
            db, login, password = request.env['res.users'].sudo().signup(
                values, token)
            res['com'] = request.cr.commit()
            res['uid'] = request.session.authenticate(db, login, password)
        except UserError as e:
            res['error'] = _(e.name or e.value)
        except (SignupError, AssertionError) as e:
            if request.env["res.users"].sudo().search([("login", "=", values.get("login"))]):
                res["error"] = _(
                    "Another user is already registered using this email address.")
            else:
                _logger.error("%s", e)
                res['error'] = _("Could not create a new account.")
        return res

    def custom_validate(self, values):
        pattern = '^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$'
        if not all([k for k in values.values()]):
            raise UserError(_("The form was not properly filled in."))
        if not re.match(pattern, values.get('login')):
            raise UserError(_("Email is not valid."))
        if not values.get('password') == values.get('confirm_password'):
            raise UserError(_("Passwords do not match, please retype again."))
        return True
