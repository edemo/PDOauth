/* 
==============================================
Back To Top Button
==============================================
*/  
 
$(window).scroll(function () {
	if ($(this).scrollTop() > 50) {
		$('#back-top').fadeIn();
	}
	else {
		$('#back-top').fadeOut();
	}
});

	// scroll body to 0px on click
$('#back-top').click(function () {
	$('#back-top a').tooltip('hide');
	$('body,html').animate({ scrollTop: 0 }, 800);
	return false;
});
      
if ($('#back-top').length!=0) $('#back-top').tooltip('hide');

export default c