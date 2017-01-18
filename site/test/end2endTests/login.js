	var PageHeaderTests = function(assert, testFrame) {
		var self=this;
		var done=assert.async();

		self.getPageName = function() {
			t=testFrame.contentWindow
			uri = t.document.URL.split("/")
			lastTag = uri[uri.length -1]
			return lastTag			
		};

		self.assertPageLoaded = function(pageName) {
			console.log("assert")
			return function() {
				console.log("before assert " + pageName)
				assert.equal(self.getPageName(), pageName)
				console.log("after assert" + pageName)
				done();
				console.log("after done" + pageName)
			}
	    };

	    self.testClickingHomeGoesToIndexHtml = function() {
			testFrame.onload=self.assertPageLoaded("index.html")
			var t=testFrame.contentWindow;
			t.document.getElementById("nav-bar-home").click()
		};
		
	    self.testClickingHowtoGoesToHowto = function() {
			testFrame.onload=self.assertPageLoaded("user_howto.html")
			var t=testFrame.contentWindow;
			t.document.getElementById("nav-bar-howto").click()
		};

	    self.testClickingLoginGoesToLogin = function() {
			testFrame.onload=self.assertPageLoaded("fiokom.html")
			var t=testFrame.contentWindow;
			console.log("before")
			t.document.getElementById("nav-bar-login").click()
			console.log("after")
		};

		return self;
	};

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
	
	QUnit.test( "clicking on home loads index.html (account)", function( assert ) {
		var callback=PageHeaderTests(assert, testFrame).testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (index)", function( assert ) {		
		var callback=PageHeaderTests(assert, testFrame).testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (about us)", function( assert ) {		
		var callback=PageHeaderTests(assert, testFrame).testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("about_us.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (user_howto)", function( assert ) {		
		var callback=PageHeaderTests(assert, testFrame).testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("user_howto.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (account)", function( assert ) {
		var callback=PageHeaderTests(assert, testFrame).testClickingHowtoGoesToHowto
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (index)", function( assert ) {
		var callback=PageHeaderTests(assert, testFrame).testClickingHowtoGoesToHowto
		tfrwrk.loadPage("index.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (about us)", function( assert ) {
		var callback=PageHeaderTests(assert, testFrame).testClickingHowtoGoesToHowto
		tfrwrk.loadPage("about_us.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (user howto)", function( assert ) {
		var callback=PageHeaderTests(assert, testFrame).testClickingHowtoGoesToHowto
		tfrwrk.loadPage("user_howto.html",callback);
	});

	QUnit.test( "clicking on login goes to login (account)", function( assert ) {
		var callback=PageHeaderTests(assert, testFrame).testClickingLoginGoesToLogin
		tfrwrk.loadPage("index.html",callback);
	});

}())

