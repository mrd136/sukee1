/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('marketplace_hyperlocal_system.wk_hyperlocal', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var defAddress = true;

    function isFacebookApp() {
        var ua = navigator.userAgent || navigator.vendor || window.opera;
        return (ua.indexOf("FBAN") > -1) || (ua.indexOf("FBAV") > -1);
    }
    function isInstagramApp() {
        var ua = navigator.userAgent || navigator.vendor || window.opera;
        var isInstagram = (ua.indexOf('Instagram') > -1) ? true : false;
        return isInstagram
    }

    $(document).ready(function() {

        $(".wk_shop_btn_trigger").on("click", function(){
            $('#wk_btn_warning').trigger('click');
        });

        if($('i.my_location').length > 0){
            $('i.my_location').removeAttr('style');
            $('div#selected-location').removeAttr('style');
        }

        $('#form_goto_shop').keydown(function(event) {
            if (event.keyCode == 13) {
                $('#wk_shop_btn').click();
                event.preventDefault();
            }
        });

        var hyperlocal_element = document.getElementById('address-for-shop');
        if (hyperlocal_element != null) {
            ajax.jsonRpc('/check/hyperlocal/enable', 'call').then(function(res) {
                var enable_hyperlocal = res["enable_hyperlocal"]
                if (res["enable_hyperlocal"])
                {
                    if (defAddress) {
                        geoFindMe();
                    }
                    google.maps.event.addDomListener(window, 'load', initAutocomplete);

                    initAutocomplete()
                    var deflocation = $('#selected-location').val();
                    $('#pac-input').bind('input propertychange', function() {
                        if ($(this).val().length == 0) {
                            $("#wk_shop_btn").attr("disabled", true);
                        }
                        else {
                            $("#wk_shop_btn").attr("disabled", false);
                        }
                    });
                }
            });
        }

        $('#wk_btn_warning').on('click', function(e) {
            var address = $('#pac-input').val();
            ajax.jsonRpc("/set/temp/location", 'call', {'location':address})
                .then(function (data) {
                    defAddress = false;
                    window.location="/get/lat/long"
                })
        });

    });

    function initAutocomplete() {
        var input = $('#pac-input').get(0);
        var searchBox = new google.maps.places.SearchBox(input);
    }

    function geoFindMe() {
        if (!navigator.geolocation){
            console.log("<p>Geolocation is not supported by your browser</p>");
        }

        function success(position) {
            var latitude  = position.coords.latitude;
            var longitude = position.coords.longitude;
            var latlng = new google.maps.LatLng(latitude, longitude);
            var geocoder = geocoder = new google.maps.Geocoder();
            geocoder.geocode({ 'latLng': latlng }, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                        var formatted_address = results[1].formatted_address;
                        ajax.jsonRpc("/set/current/location", 'call', {'location':formatted_address,'latitude':latitude,'longitude':longitude})
                            .then(function (data) {
                                if (data) {
                                    $('#pac-input').val(formatted_address);
                                    $('#selected-location').text(formatted_address);
                                    defAddress = false;
                                }
                            })
                    }
                }

            });
        }
        function error() {
            console.log("Unable to retrieve your location");
        }

        if(navigator.geolocation && !isFacebookApp() && !isInstagramApp()){navigator.geolocation.getCurrentPosition(success, error);}
    }

})
