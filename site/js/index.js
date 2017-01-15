(function(){	
	var self;
	PageScript.prototype.page = "index";

	PageScript.prototype.main = function() {
		self=this.getThis()
		self.ajaxget( "/adauris", self.callback(self.commonInit) )
		if ($.fn.owlCarousel) {
			$("#owl-demo").owlCarousel({
				navigation : true, // Show next and prev buttons
				navigationText: [
					"<i class='fa fa-angle-left'></i>",
					"<i class='fa fa-angle-right'></i>"
				],
				slideSpeed : 300,
				paginationSpeed : 400,
				autoPlay: true,  
				items : 4,
				itemsDesktop:[1199,4],  
				itemsDesktopSmall:[979,3],  //As above.
				itemsTablet:[768,3],    //As above.
				itemsTablet:[640,2],   
				itemsMobile:[479,1],    //As above
				goToFirst: true,    //Slide to first item if autoPlay reach end
				goToFirstSpeed:1000 
			});
		}
	}

	PageScript.prototype.initialise = function() {
		self.ajaxget("/v1/users/me", self.initCallback)
		if (document.getElementById("counter_area")) self.getStatistics()
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		self.isLoggedIn = (status == 200)
		self.refreshTheNavbar()
	}
	
	PageScript.prototype.getStatistics=function(){
		this.ajaxget("/v1/statistics", self.callback(self.statCallback))
	}
	
	PageScript.prototype.statCallback=function(text) {
		data=JSON.parse(text)
		document.getElementById("user-counter").innerHTML=(data.users)?data.users:0
		document.getElementById("magyar-counter").innerHTML=(data.assurances.magyar)?data.assurances.magyar:0
		document.getElementById("assurer-counter").innerHTML=(data.assurances.assurer)?data.assurances.assurer:0
		document.getElementById("application-counter").innerHTML=(data.applications)?data.applications:0
		//init counter if data presents
		$('.counter').counterUp({
			delay: 100,
			time: 2000
		});
	}
})();


/*!
* jquery.counterup.js 1.0
*
* Copyright 2013, Benjamin Intal http://gambit.ph @bfintal
* Released under the GPL v2 License
*
* Date: Nov 26, 2013
*/


(function( $ ){
  "use strict";

  $.fn.counterUp = function( options ) {

    // Defaults
    var settings = $.extend({
        'time': 400,
        'delay': 10
    }, options);

    return this.each(function(){

        // Store the object
        var $this = $(this);
        var $settings = settings;
		var $triggered = false

        var counterUpper = function() {
			if ($triggered) return
            var nums = [];
            var divisions = $settings.time / $settings.delay;
            var num = $this.text();
            var isComma = /[0-9]+,[0-9]+/.test(num);
            num = num.replace(/,/g, '');
            var isInt = /^[0-9]+$/.test(num);
            var isFloat = /^[0-9]+\.[0-9]+$/.test(num);
            var decimalPlaces = isFloat ? (num.split('.')[1] || []).length : 0;

            // Generate list of incremental numbers to display
            for (var i = divisions; i >= 1; i--) {

                // Preserve as int if input was int
                var newNum = parseInt(num / divisions * i);

                // Preserve float if input was float
                if (isFloat) {
                    newNum = parseFloat(num / divisions * i).toFixed(decimalPlaces);
                }

                // Preserve commas if input had commas
                if (isComma) {
                    while (/(\d+)(\d{3})/.test(newNum.toString())) {
                        newNum = newNum.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
                    }
                }

                nums.unshift(newNum);
            }

            $this.data('counterup-nums', nums);
            $this.text('0');

            // Updates the number until we're done
            var f = function() {
                $this.text($this.data('counterup-nums').shift());
                if ($this.data('counterup-nums').length) {
                    setTimeout($this.data('counterup-func'), $settings.delay);
                } else {
                    delete $this.data('counterup-nums');
                    $this.data('counterup-nums', null);
                    $this.data('counterup-func', null);
                }
            };
            $this.data('counterup-func', f);

            // Start the count up
            setTimeout($this.data('counterup-func'), $settings.delay);
			$triggered=true
        };

        // Perform counts when the element gets into view
        $this.waypoint(counterUpper, { offset: '100%', triggerOnce: false });
    });

  };

})( jQuery );