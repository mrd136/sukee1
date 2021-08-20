odoo.define('website_guest_checkout.website_guest_checkout', function (require) {
	var ajax = require('web.ajax');
	$(document).ready(function () {
		$('#wk_guest_checkout').on('click', function (event) {
			var uid = $(this).data('uid');
			var p_uid = $(this).data('p_uid');
			if (uid == p_uid) {
				custom_popover(event, $('#div_checkout'), true);
				$('#div_checkout').popover('show');
				if ($(this).data('allow_uninvited') == 'b2c') {
					$('#signup_tab').show();
				}
				event.preventDefault();
			} else {
				window.location= '/shop/checkout?express=1';
			}
		});
		$('#wk_guest_checkout_main').on('click', function (event) {
			var uid = $(this).data('uid');
			var p_uid = $(this).data('p_uid');
			if (uid == p_uid) {
				event.preventDefault();
				custom_popover(event, $('#div_checkout_main'), true);
				$('#div_checkout_main').popover('show');
				if ($(this).data('allow_uninvited') == 'b2c') {
					$('#signup_tab').show();
				}
				
			} else {
				window.location= '/shop/checkout?express=1';
			}
		});
		$('#wk_guest_checkout_main_2').on('click', function (event) {
			var uid = $(this).data('uid');
			var p_uid = $(this).data('p_uid');
			if (uid == p_uid) {
				custom_popover(event, $('#div_checkout_main_2'), true);
				$('#div_checkout_main_2').popover('show');
				if ($(this).data('allow_uninvited') == 'b2c') {
					$('#signup_tab').show();
				}
				event.preventDefault();
			} else {
				$(location).attr('href', '/shop/checkout');
			}
		});
		function custom_popover(event, element_id, status) {
			element_id.popover({
					trigger: 'manual',
					container: 'body',
					template: '<div class="popover guest-checkout-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>',
					placement: 'bottom',
					animation: true,
					html: true,
					sanitize: false,
					content: `	<div class="panel-body text-center wk_guest_checkout_pop">
									<div>
										<button  id="popover_close" class="close  btn-default" aria-label="Close" style="float:right" >X</button>
										<h4 class="check_login_error"><p class="text-primary">For Further Processing.</p></h4>
										<ul class="nav nav-tabs" style="margin: 5%;border-bottom: 0px solid #dee2e6;">
											<li id="login_tab" ><a data-toggle="tab" href="#check_login"><b>Sign In</b></a></li>
											<li id="signup_tab" style="display:none;margin-left: 5%;"><a data-toggle="tab" href="#check_signup"><b>Sign Up</b></a></li>
										</ul>
										<div class="tab-content">
											<div id="check_login" class="tab-pane fade show active">
												<form class="form" role="form">
													<div class="form-group demo_checkout_login_class">
														<label class="sr-only" for="wk_signin_email">Email address</label>
														<input class="form-control" id="wk_signin_email" placeholder="Enter email" type="email"/>
													</div>
													<div class="form-group demo_checkout_login_class">
														<label class="sr-only" for="wk_signin_psw">Password</label>
														<input class="form-control" id="wk_signin_psw" placeholder="Password" type="password"/>
													</div>
													<button id="submit_sign" type="button" class="btn btn-primary" title=""><b>Sign in</b></button>
												</form>
											</div>
											<div id="check_signup" class="tab-pane fade">
												<form class="" role="form">
													<div class="form-group demo_checkout_sign_up_class">
														<label class="sr-only" for="wk_signup_un">User Name</label>
														<input class="form-control" id="wk_signup_un" placeholder="User" type="text"/>
													</div>
													<div class="form-group demo_checkout_sign_up_class">
														<label class="sr-only" for="wk_signup_email">Email address</label>
														<input class="form-control" id="wk_signup_email" placeholder="Enter email" type="text"/>
													</div>
													<div class="form-group demo_checkout_sign_up_class">
														<label class="sr-only" for="wk_signup_psw">Password</label>
														<input class="form-control" id="wk_signup_psw" placeholder="Password" type="password"/>
													</div>
													<div class="form-group demo_checkout_sign_up_class">
														<label class="sr-only" for="wk_signup_cpsw">confirm Password</label>
														<input class="form-control" id="wk_signup_cpsw" placeholder="Confirm Password" type="password"/>
													</div>
													<button id="submit_signup" type="button" class="btn btn-primary" title=""><b>Sign up</b></button>
												</form>
											</div>
										</div>
									</div>
								</div>`,

				});
		}


		$(document).on('click', '#popover_close', function () {
			$('#div_checkout').popover('hide');
			$('#div_checkout_main').popover('hide');
			$('#div_checkout_main_2').popover('hide');
		});
		$(document).on('click', '#popover_close', function () {
			$('#div_checkout').popover('hide');
		});
		function custom_msg(element_id, status, msg) {
			if (status == true) {
				element_id.empty().append("<div class='alert alert-danger text-center' id='Wk_err'>" + msg + "<button type='button' class='close' data-dismiss='alert' aria-label='Close'> <span class='res glyphicon glyphicon-remove ' aria-hidden='true'></span></button></div>");
			}
			if (status == false)
				element_id.empty();
			return true;
		}
		function custom_mark(element_id, status) {
			if (status == true)
				element_id
					.parent()
					.addClass('has-error has-feedback');
		}

		$(document).on('click', '#submit_sign', function () {
			var db = $('#wk_database');
			var email = $('#wk_signin_email');
			var psw = $('#wk_signin_psw');
			var input = { login: email.val(), password: psw.val(), db: db.val() };
			ajax.jsonRpc('/checkout/login/', 'call', input)
				.then(function (response) {
					if (response.uid != false) {
						$(location).attr('href', '/shop/checkout');
					}
					else {
						console.log("wk_login_error");
						custom_mark($('.demo_checkout_login_class'), true);
						$('.check_login_error').empty().append("Incorrect username or password.");
					}
				});

		});

		$(document).on('click', '#submit_signup', function () {
			var name = $('#wk_signup_un');
			var db = $('#wk_database');
			var login = $('#wk_signup_email');
			var password = $('#wk_signup_psw');
			var confirm_password = $('#wk_signup_cpsw');
			var data = {
				'login': login.val(),
				'password': password.val(), confirm_password: confirm_password.val(),
				'db': 'test24',
				name: name.val(),
				redirect: '/shop'
			};
			ajax.jsonRpc('/checkout/signup/', 'call', data)
				.then(function (res) {
					console.log(res);
					if (typeof (res['uid']) != "undefined") {
						$(location).attr('href', '/shop/checkout');
					} else {
						$('.check_login_error').empty().append(res['error']);
						var a = jQuery("#check_signup input:text[value=''] ,#check_signup input:password[value='']");
						a.each(function (index) {
							$(this).parent()
								.addClass('has-error has-feedback')
								.append("<span class='glyphicon glyphicon-remove form-control-feedback'></span>");

						});
					}
				});
		});


	});

});
