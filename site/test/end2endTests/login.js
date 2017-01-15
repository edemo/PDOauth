
(function(){
	var testFrame=document.getElementById('testarea')
	var t
	if ( (testFrame) && (t=testFrame.contentWindow) ) {}
	else return

	var PageHeaderTests = function(assert, done, testFrame) {
		var self=this;
		
		self.getLastTag = function() {
			console.log("getLastTag")
			t=testFrame.contentWindow
			uri = t.document.URL.split("/")
			lastTag = uri[uri.length -1]
			return lastTag			
		};
		self.assertIndexHtmlLoaded = function() {
			console.log("assertIndexHtmlLoaded")
			assert.equal(self.getLastTag(), "index.html")
			done();
	    };
	    self.testClickingHomeGoesToIndexHtml = function() {
			console.log("testClickingHomeGoesToIndexHtml")
			testFrame.onload=self.assertIndexHtmlLoaded
			var t=testFrame.contentWindow;
			t.document.getElementById("nav-bar-home").click()
		};
		return self;
	}

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
	
	QUnit.test( "clicking on home loads index.html", function( assert ) {		
		var done=assert.async();
		var callback=PageHeaderTests(assert, done, testFrame).testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (about us)", function( assert ) {		
		var done=assert.async();
		var callback=PageHeaderTests(assert, done, testFrame).testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("about_us.html",callback);
	});

}())

