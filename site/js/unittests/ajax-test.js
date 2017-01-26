
import ajax from ../modules/ajax.js
export function ajax_test(){
	
	QUnit.module( "AJAX" ); 
	
	var commonAjaxTestMethods = function(me){
			me.send = function(data) {
				pageScript.callback = me.callback 
				pageScript.data = data
			}
			me.open = function( method, uri, async ) {
				pageScript.method = method
				pageScript.uri = uri
				pageScript.async = async
			}
			me.setRequestHeader = function( name, value) {
				pageScript.header_name = name
				pageScript.header_value = value
			}
		},
		testXMLHttpRequestObject = function( arg ) {
			var me = this;
			this.oName = "XMLHttpRequest"
			this.arg=arg || "undefined";
			commonAjaxTestMethods( me )
		},
		testActiveXHttpRequestObject = function(arg) {
			var me = this;
			this.arg=arg || "undefined";
			this.oName="ActiveXObject"
			commonAjaxTestMethods(me)
		},
		test = {
			win: {
				XMLHttpRequest: testXMLHttpRequestObject,
//				location: window.location
				},
			debug: true,
			uribase: "/ada",
			reportServerFailure: function(){},
			displayServerResponse: function(){}
		}

	QUnit.test( "ajaxbase() should return with a xmlhttp object - IE style httpRequest", function( assert ) {
			// Initializing test	
		var	test = {
			win: {
				XMLHttpRequest: testXMLHttpRequestObject,
//				location: window.location
				},
			debug: true,
			uribase: "/ada",
			reportServerFailure: function(){},
			displayServerResponse: function(){}
		}
		var AJAX = new ajax(test)
		delete test.win.XMLHttpRequest							
		test.win.ActiveXObject= testActiveXHttpRequestObject	// IE style httpRequest
			// calling the unit
		var xmlhttp_testobject = pageScript.ajaxBase(callbackForAJAXtest);
			// asserts	
		assert.equal(xmlhttp_testobject.oName, "ActiveXObject", "if XMLHttpRequest isn't defined, should return with an 'ActiveXObject' ");
		assert.equal(xmlhttp_testobject.arg, "Microsoft.XMLHTTP", "ActiveXObject calling argument should be 'Microsoft.XMLHTTP'");
			// cleaning environment
		test.win.XMLHttpRequest= testXMLHttpRequestObject; // setting back for standard non IE style httpRequest
	});

QUnit.test( "ajaxbase() should return with a xmlhttp object - non IE style httpRequest", function( assert ) {	
		// Initializing test
	pageScript = new PageScript(test)
		// calling the unit
	var xmlhttp_testobject = pageScript.ajaxBase(callbackForAJAXtest);
		// asserts
	assert.equal(xmlhttp_testobject.oName, "XMLHttpRequest", "if XMLHttpRequest defined, should return with an 'XMLHttpRequest' ");
	assert.equal(xmlhttp_testobject.arg, "undefined", "XMLHttpRequest call shouldn't have any argument");
});

QUnit.test( "xmlhttp.onreadystatechange() should call the callback according the value of the 'readyState' property", function( assert ) {	
		// Initializing the test
	pageScript = new PageScript(test)
	var xmlhttp_testobject = pageScript.ajaxBase(callbackForAJAXtest);
	xmlhttp_testobject.status = 201
	xmlhttp_testobject.responseText = "szia";
	xmlhttp_testobject.responseXML = "xmlData";
		// test setup 1.
	xmlhttp_testobject.readyState=1
		// calling the unit	
	xmlhttp_testobject.onreadystatechange(); 
		// asserts	
	assert.notOk(pageScript.callbackArgs, "callback shouldn't be called")
	
		// test setup 2.	
	xmlhttp_testobject.readyState=4
		// calling the unit	
	xmlhttp_testobject.onreadystatechange(); 
		// asserts 
	assert.ok(pageScript.callbackArgs, "callback should be called");
	assert.ok(( pageScript.callbackArgs.status==201 && 
				pageScript.callbackArgs.text=="szia" &&
				pageScript.callbackArgs.xml=="xmlData" ),
				"the callback arguments should contain the given values");
});

QUnit.test( "ajaxpost() can be mocked", function( assert ) {
		// Initializing the test	
	pageScript = new PageScript(test);
	var testUrl = "/my_url";
	var _uribase = pageScript.uribase;
	pageScript.uribase = "base.uri.com";
		// calling the unit		
	pageScript.ajaxpost( testUrl, {data: "hello", name: "world"}, callbackForAJAXtest );
		// asserts 
	assert.ok(( pageScript.uri == pageScript.uribase + testUrl &&
				pageScript.method == "POST" &&
				pageScript.async === true),
				"xmlhttp.open should be called with method='POST', url and async=true");
	assert.ok(( pageScript.header_name == "Content-type" && 
				pageScript.header_value == "application/x-www-form-urlencoded" ),
				"xmlhttp.setRequestHeader() should be called with data" );
	assert.equal( pageScript.data, "data=hello&name=world", "xmlhttp.send should be called with a message in its argument" );
	assert.equal( pageScript.callback.toString(), callbackForAJAXtest.toString(), "xmlhttp object should have the callback" );
		// cleaning
	pageScript.uribase = _uribase;
});

QUnit.test( "ajaxget() can be mocked", function( assert ) {
		// Initializing the test		
	pageScript = new PageScript(test)
	var testUrl = "/my_url";
	var _uribase = pageScript.uribase;
	pageScript.uribase = "base.uri.com";
		// calling the unit		
	pageScript.ajaxget( testUrl, callbackForAJAXtest );
		// asserts 
	assert.ok(( pageScript.uri == pageScript.uribase + testUrl &&
				pageScript.method == "GET" &&
				pageScript.async === true ),
				"xmlhttp.open should be called with method='GET', url and async=true");
	assert.notOk( pageScript.data, "xmlhttp.open should be called without args" );
	assert.equal( pageScript.callback.toString(), callbackForAJAXtest.toString(), "xmlhttp object should have the callback" );
		// cleaning
	pageScript.uribase = _uribase;
});

}
