
(function(){
	var testFrame=document.getElementById('testarea')
	var t
	if ( (testFrame) && (t=testFrame.contentWindow) ) {}
	else return
	
	QUnit.module( "login" ); 	
	QUnit.test( "loading fiokom.html", function( assert ) {
		var done=assert.async()
		var callback=function(){
			assert.equal( t.document.title,"ADA - fiókom", "loaded page should be fiokom.html" )
			done()
		}  												// ha el tudjuk kapni a callback-et, akkor beletesszük az assert-eket
		tfrwrk.loadPage("fiokom.html",callback);
	});

}())

