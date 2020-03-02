// Custom Js for delete button in cart on header
odoo.define('sasmar_theme.custom_js', function (require) {
"use strict";

	var ajax = require('web.ajax');
	$(document).ready(function() {
		$('.oe_website_sale').each(function() {
			var oe_website_sale = this;

			//$(".oe_cart input.js_quantity").change(function(){
			//    setTimeout("location.reload();", 100);
			//});
			
			$(".js_add_cart_json_new").click(function(ev){
				ev.preventDefault();
				var $link = $(ev.currentTarget);
				var $input = $link.parent().parent().find("input");
				var value = parseInt(0, 10);
				var line_id = parseInt($input.data('line-id'), 10);
				if (isNaN(value)) value = 0;
				ajax.jsonRpc("/shop/cart/update_json", 'call', {
						'line_id': line_id,
						'product_id': parseInt($input.data('product-id'), 10),
						'set_qty': value
					})
					.then(function(data) {
						if (!data.quantity) {
							location.reload();
							return;
						}
					});
			});
		});

		$("body").on('click','.clear_cart',function (ev){
			ev.preventDefault();
			ajax.jsonRpc("/shop/cart/clear_cart", 'call', {})
			.then(function (data) {
						location.reload();
						return;
			});
			return false;
		});

		// var sticky = $('.navbar-expand-md').offsetTop;

		// if (window.pageYOffset >= sticky) {
		// 	navbar.classList.add("navbar-fixed-top");
		// 	$('div .hdr').addClass('d-none'); 
		// } else {
		// 	navbar.classList.remove("navbar-fixed-top");
		// 	$('div .hdr').removeClass('d-none'); 
		// }

		// if($("#wrapwrap").find('main .bi_homepage_main').length !== 0){
		// 	this.$target.css({
		// 		'position': 'absolute',
		// 	})
		// 	this.$target.find('nav').css('cssText','background-color:transparent !important')
		// 	this.$target.find('a.nav-link').css('cssText','color:white !important;font-size: 19x;')
		// 	this.$target.find('a.nav-link').hover(function(){
		// 		$(this).css('cssText','border-bottom: solid #3498db 0px;');
		// 	},function(){
		// 		$(this).css('cssText','background-color:transparent !important;color:white !important;')
		// 	});
		// 	this.$target.find('span.logo1').css('cssText','color:white !important')
		// 	this.$target.find('span.logo3').css('cssText','color:white !important')
		// 	this.$target.find('.dropdown-menu').addClass('dropdown-menu-left')
		// 	this.$target.find('.dropdown-menu').css('cssText','background-color:transparent !important;border : 0 !important;left: 0;right: auto')
		// 	this.$target.find('a.dropdown-item').css('cssText','color:white !important;font-size: 15px;')
		// 	this.$target.find('a.dropdown-item').hover(function(){
		// 		$(this).css('cssText','background-color:black !important;color:white !important;font-size: 16px;')
		// 	}, function(){
		// 		$(this).css('cssText','background-color:transparent !important;color:white !important;font-size: 16px;');
		// 	});
		// }
	});




});

//loader
$(window).load(function() {
	$(".se-pre-con").fadeOut("slow");;
});

// header fix
$(window).scroll(function() {
	if ($(window).scrollTop() > 50) {
		$('.navbar-expand-md').addClass('navbar-fixed-top');
	   	$('div .hdr').addClass('d-none'); 
	} else {
		$('.navbar-expand-md').removeClass('navbar-fixed-top');
	   	$('div .hdr').removeClass('d-none'); 
	}
});

// $(window).scroll(function(){
// 	// Get the offset position of the navbar
// 	var sticky = $(".navbar-expand-md").offset().top;
// 	console.log(window.pageYOffset,"//////////////////////////",sticky)
// 	if (window.pageYOffset > 50) {
// 		$('.navbar-expand-md').addClass('navbar-fixed-top');
// 	   	$('div .hdr').addClass('d-none'); 
// 	} else {
// 		$('.navbar-expand-md').removeClass('navbar-fixed-top');
// 	   	$('div .hdr').removeClass('d-none'); 
// 	}

// 	// if ($(window).scrollTop() >= 100 ) {
// 	//    $('.navbar-expand-md').addClass('navbar-fixed-top');
// 	//    $('div .hdr').addClass('d-none'); 
// 	// }
// 	// else {
// 	//    $('.navbar-expand-md').removeClass('navbar-fixed-top');
// 	//    $('div .hdr').removeClass('d-none'); 
// 	// }
// });

// Search Custom Js For Header    	
$(document).ready(function(){
	$(".search-area").click(function(){
		$(".searchform").toggle();
	});
});

$(document).ready(function() {
  var $searchlink = $('#searchlink');
  // hover effect
  $searchlink.on('mouseover', function(){
	console.log("OPennnnnnnn")
	$(this).addClass('open');
  }).on('mouseout', function(){
	$(this).removeClass('open');
  });
});   


// Video Custom JS 
$(document).ready(function () {

	$(".player").mb_YTPlayer();

});


 
	
