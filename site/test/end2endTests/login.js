import PageHeaderTests from "./modules/PageHeaderTests.js"

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
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (index)", function( assert ) {		
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (about us)", function( assert ) {		
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("about_us.html",callback);
	});

	QUnit.test( "clicking on home loads index.html (user_howto)", function( assert ) {		
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHomeGoesToIndexHtml
		tfrwrk.loadPage("user_howto.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (account)", function( assert ) {
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHowtoGoesToHowto
		tfrwrk.loadPage("fiokom.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (index)", function( assert ) {
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHowtoGoesToHowto
		tfrwrk.loadPage("index.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (about us)", function( assert ) {
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHowtoGoesToHowto
		tfrwrk.loadPage("about_us.html",callback);
	});

	QUnit.test( "clicking on howto loads user_howto.html (user howto)", function( assert ) {
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingHowtoGoesToHowto
		tfrwrk.loadPage("user_howto.html",callback);
	});

/*
	QUnit.test( "clicking on login goes to login (account)", function( assert ) {
		var tester = new PageHeaderTests(assert, testFrame)
		var callback=tester.testClickingLoginGoesToLogin
		tfrwrk.loadPage("index.html",callback);
	});
*/

}())

