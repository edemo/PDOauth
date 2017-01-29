import { pageScript } from './modules/index'
import x from './modules/back_to_top' //back to top button

	//setting up owl Carousel
$(document).ready(pageScript.main)
	
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