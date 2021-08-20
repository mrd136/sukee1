# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from . import models
from . import controllers
from odoo.addons.payment.models.payment_acquirer import create_missing_journal_for_acquirers
# from odoo.addons.payment import reset_payment_provider
#
# def uninstall_hook(cr, registry):
#     reset_payment_provider(cr, registry, 'xendit_ewallets')

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='13.0':raise Warning('Module support Odoo series 13.0 found {}.'.format(server_serie))
    return True
