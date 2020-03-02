$(document).ready(function(){
	//console.log("New Js")
    $(".search-area").click(function(){
        $(".searchform").toggle();
    });
});



    $('#myCarousel').carousel();
    var winWidth = $(window).innerWidth();
    $(window).resize(function () {

        if ($(window).innerWidth() < winWidth) {
            $('.carousel-inner>.item>img').css({
                'min-width': winWidth, 'width': winWidth
            });
        }
        else {
            winWidth = $(window).innerWidth();
            $('.carousel-inner>.item>img').css({
                'min-width': '', 'width': ''
            });
        }
    });



/*$(document).ready(function(){
	console.log("New")
    $(".search-area").click(function(){
    	$(".block-search").addClass("show");
        $(".block-search").toggle();
    });
});*/

/* Slider JS */
 $(document).ready(function() {
       $("#banner-slider-demo-11").owlCarousel({
            items: 1,
            autoplay: true,
            autoplayTimeout: 5000,
            autoplayHoverPause: true,
            dots: false,
            nav: true,
            navRewind: true,
            animateIn: 'fadeIn',
            animateOut: 'fadeOut',
            loop: true
            
        });
    });/* navText: ["<em class='porto-icon-chevron-left'></em>","<em class='porto-icon-chevron-right'></em>"], */



$(document).ready(function() {
            $('#custom-owl-slider-product.owl-carousel').owlCarousel({
                items:1,
                lazyLoad:true
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


// Registration page custom Js

/*
function optionCheck(){
        var option = document.getElementById("type").value;
        if(option == "consumer"){
        
        	document.getElementById("your_email").style.visibility ="visible";
            document.getElementById("your_email").style.display ="block";
            
            document.getElementById("your_name").style.visibility ="visible";
            document.getElementById("your_name").style.display ="block";
            
            document.getElementById("your_password").style.visibility ="visible";
            document.getElementById("your_password").style.display ="block";
            
            document.getElementById("confirm_password").style.visibility ="visible";
            document.getElementById("confirm_password").style.display ="block";
            
            document.getElementById("your_email").style.visibility ="visible";
            document.getElementById("your_email").style.display ="block";

        }
        if(option == "wholesaler"){
        	
        	document.getElementById("your_password").style.visibility ="hidden";
            document.getElementById("your_password").style.display ="none";
            
            document.getElementById("confirm_password").style.visibility ="hidden";
            document.getElementById("confirm_password").style.display ="none";
            
        }
    }
*/


