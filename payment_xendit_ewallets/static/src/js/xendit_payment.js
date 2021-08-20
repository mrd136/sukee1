/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('payment_xendit_ewallets.xendit_ewallets', function (require) {
    "use strict";

    var PaymentForm = require('payment.payment_form');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    PaymentForm.include({

        payEvent: function (ev) {
            ev.preventDefault();
            var self = this;
            var checked_radio = this.$('input[type="radio"]:checked');
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            if (ev.type === 'submit') {
                var button = $(ev.target).find('*[type="submit"]')[0]
            } else {
                var button = ev.target;
            }

            if (checked_radio.length === 1 && this.isFormPaymentRadio(checked_radio) && checked_radio.data('provider') === 'xendit_ewallets') {
                this.disableButton(button);
                var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
                var acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
                // if there's a prepare tx url set
                if ($tx_url.length === 1) {
                    return this._rpc({
                        route: $tx_url[0].value,
                        params: {
                            'acquirer_id': parseInt(acquirer_id),
                            'access_token': self.options.accessToken,
                            'success_url': self.options.successUrl,
                            'error_url': self.options.errorUrl,
                            'callback_method': self.options.callbackMethod,
                            'order_id': self.options.orderId,
                        },
                    }).then(function (result) {
                        if (result) {
                            var newForm = document.createElement('div');
                            newForm.innerHTML = result;
                            var xendit_error_msg = $(newForm).find('input[name="xendit_error_msg"]').val()
                            var xendit_redirect_url = $(newForm).find('input[name="xendit_redirect_url"]').val()
                            console.log("-------------",xendit_error_msg,"------",xendit_redirect_url,"-------------");
                            if(xendit_error_msg){
                                self.displayError(
                                    _t('Xendit API Error'),
                                    _t(xendit_error_msg)
                                );
                                self.enableButton(button);
                            }
                            else{
                                if(xendit_redirect_url){
                                    window.location = xendit_redirect_url;
                                }
                                else{
                                    self.displayError(
                                        _t('Server Error'),
                                        _t("We are not able to redirect you to the payment form.")
                                    );
                                    self.enableButton(button);
                                }
                            }
                            return {
                                amount : $(newForm).find('input[name="amount"]').val(),
                            }
                        }
                        else {
                            self.displayError(
                                _t('Server Error'),
                                _t("We are not able to redirect you to the payment form.")
                            );
                            self.enableButton(button);
                        }
                    }).guardedCatch(function (error) {
                        error.event.preventDefault();
                        self.displayError(
                            _t('Server Error'),
                            _t("We are not able to redirect you to the payment form.") + " " +
                                self._parseError(error)
                        );
                    });
                }
                else {
                    // we append the form to the body and send it.
                    this.displayError(
                        _t("Cannot setup the payment"),
                        _t("We're unable to process your payment.")
                    );
                    self.enableButton(button);
                }
            }
            else {
                return this._super.apply(this, arguments);
            }
        }

    });
});
