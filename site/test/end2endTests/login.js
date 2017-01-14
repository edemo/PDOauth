
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
		}
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "loading index.html", function( assert ) {
		var done=assert.async()
		var callback=function(){
			assert.equal( t.document.title,"ADA - anonim digitális azonosító")
			done()
		}
		tfrwrk.loadPage("index.html",callback);
	});

	function PageHeaderTests(assert) {
		this.theTest = function() {
			t=testFrame.contentWindow
			uri = t.document.URL.split("/")
			lastTag = uri[uri.length -1]
			assert.equal(lastTag, "index.html")
			start();
	    }
	}

	QUnit.test( "clicking on home loads index.html", function( assert ) {
		var done=assert.async()
		var callback=function(){
			t.document.getElementById("nav-bar-home").click()
			    stop();
				testFrame.onload=PageHeaderTests(assert).theTest
			done()
		}
		tfrwrk.loadPage("fiokom.html",callback);
	});

}())

