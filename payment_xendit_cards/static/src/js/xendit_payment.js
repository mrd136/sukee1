/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('payment_xendit_cards.xendit_cards', function (require) {
    "use strict";

    var PaymentForm = require('payment.payment_form');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    function xenditAuthenticationHandler(err, creditCardToken){
        var ifr = document.getElementById("xenCardIframe");
        if(ifr){
            $('#xendit_frame').hide();
            ifr.parentNode.removeChild(ifr);
        }
        if (err) {
            alert(err.message);
            return;
        }
        if (creditCardToken.status === 'VERIFIED') {
            var data = {
                "id": creditCardToken.credit_card_token_id,
                "authentication_id": creditCardToken.id,
                "masked_card_number": creditCardToken.masked_card_number
            }
            ajax.jsonRpc('/xendit/cards/create/token', 'call', data)
                .then(function (result) {
                    window.location = result;
                });
        }
        else if (creditCardToken.status === 'IN_REVIEW') {
            var iframe = document.createElement('iframe');
            iframe.src = creditCardToken.payer_authentication_url
            iframe.setAttribute("id","xenCardIframe");
            iframe.setAttribute("style","height:450px;width:550px;");
            var xendit_frame = document.getElementById("xendit_frame");
            xendit_frame.appendChild(iframe);
            $('#xendit_frame').show();
        }
        else if (creditCardToken.status === 'FAILED') {
            alert(creditCardToken.failure_reason);
        }
    }

    function xenditResponseHandler(err, creditCardToken){
        var ifr = document.getElementById("xenCardIframe");
        if(ifr){
            $('#xendit_frame').hide();
            ifr.parentNode.removeChild(ifr);
        }
        if (err) {
            alert(err.message);
            return;
        }
        if (creditCardToken.status === 'VERIFIED') {
            if(!creditCardToken.authentication_id){
                var form = $('form.o_payment_form');
                var order_amt = form.find('input[name="amount_total"]');
                Xendit.card.createAuthentication({
                    "amount": order_amt.val(),
                    "token_id": creditCardToken.id
                }, xenditAuthenticationHandler);
                return
            }
            else{
                ajax.jsonRpc('/xendit/cards/create/token', 'call', creditCardToken)
                    .then(function (result) {
                        window.location = result;
                    });
            }
        }
        else if (creditCardToken.status === 'IN_REVIEW') {
            var iframe = document.createElement('iframe');
            iframe.src = creditCardToken.payer_authentication_url
            iframe.setAttribute("id","xenCardIframe");
            iframe.setAttribute("style","height:450px;width:550px;");
            var xendit_frame = document.getElementById("xendit_frame");
            xendit_frame.appendChild(iframe);
            $(xendit_frame).show();
        }
        else if (creditCardToken.status === 'FAILED') {
            alert(creditCardToken.failure_reason);
        }
    }


    PaymentForm.include({

        payEvent: function (ev) {
            ev.preventDefault();
            var $checkedRadio = this.$('input[type="radio"]:checked');
            if (ev.type === 'submit') {
                var button = $(ev.target).find('*[type="submit"]')[0]
            } else {
                var button = ev.target;
            }
            if ($checkedRadio.length === 1 && this.isNewPaymentRadio($checkedRadio) && $checkedRadio.data('provider') === 'xendit_cards') {
                if (this.options.partnerId === undefined) {
                    console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
                }
                var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
                var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
                var inputsForm = $('input', acquirerForm);
                var formData = this.getFormData(inputsForm);
                var wrong_input = false;

                inputsForm.toArray().forEach(function (element) {
                    //skip the check of non visible inputs
                    if ($(element).attr('type') == 'hidden') {
                        return true;
                    }
                    $(element).closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
                    $(element).siblings( ".o_invalid_field" ).remove();
                    //force check of forms validity (useful for Firefox that refill forms automatically on f5)
                    $(element).trigger("focusout");
                    if (element.dataset.isRequired && element.value.length === 0) {
                            $(element).closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                            $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                            wrong_input = true;
                    }
                    else if ($(element).closest('div.form-group').hasClass('o_has_error')) {
                        wrong_input = true;
                        $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                    }
                });

                if (wrong_input) {
                    return;
                }

                this.disableButton(button);

                var number = formData.cc_number.replace(/\s+/g, '');
                var expr = formData.cc_expiry.replace(/\s+/g, '');
                expr = expr.split("/")
                Xendit.card.createToken({
                    amount: formData.amount_total,
                    card_number: number,
                    card_exp_month: expr[0],
                    card_exp_year: expr[1],
                    card_cvn: formData.cc_cvc,
                    is_multiple_use: false,
                    should_authenticate: true
                }, xenditResponseHandler);
            }
            else {
                return this._super.apply(this, arguments);
            }
        },
    });
});
