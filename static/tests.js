function xmlFor(text) {

	if (window.DOMParser) {
		parser=new DOMParser();
		xmlDoc=parser.parseFromString(text,"text/xml");
	} else {
		xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
		xmlDoc.async=false;
		xmlDoc.loadXML(text);
	}  
	return xmlDoc;
}

commonAjaxTestMethods = function(me){

	me.send = function(data) {
		pageScript.callback = me.callback 
		pageScript.data = data
//		me.callback(pageScript.status,pageScript.text,pageScript.xml);
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
}

testXMLHttpRequestObject = function( arg ) {

	var me = this;
	this.oName = "XMLHttpRequest"
	this.arg=arg || "undefined";
	commonAjaxTestMethods(me)
}

testActiveXHttpRequestObject = function(arg) {
	var me = this;
	this.arg=arg || "undefined";
	this.oName="ActiveXObject"
	commonAjaxTestMethods(me)
}

hidePopup = function () {  // hides and clears the modal div
	document.getElementById("PopupWindow_TitleDiv").innerHTML   = "";
	document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
	document.getElementById("PopupWindow_MessageDiv").innerHTML = "";
	document.getElementById("PopupWindow_SuccessDiv").innerHTML = "";
	document.getElementById('popup').style.display = 'none';
	document.getElementById('fade').style.display  = 'none';
}

isPopupShown = function() { return document.getElementById("popup").style.display=="flex"; }
isPopupHidden = function() { return document.getElementById("popup").style.display!="flex"; }

isLoginButtonHidden        = function() { return document.getElementById("login-menu").style.display=="none" }
isRegistrationButtonHidden = function() { return document.getElementById("registration-menu").style.display=="none" }
isAssurerButtonHidden      = function() { return document.getElementById("assurer-menu").style.display=="none" }
isAccountButtonHidden      = function() { return document.getElementById("account-menu").style.display=="none" }
isApplicationButtonHidden  = function() { return document.getElementById("application-menu").style.display=="none" }
isCredentialContainerEmpty = function() { console.log(document.getElementById("Remove_Credential_Container").innerHTML); return document.getElementById("Remove_Credential_Container").innerHTML==""}
doesContainerContain = function(container,testStrings) {
	for(testString in testStrings){
		if (!document.getElementById(container).innerHTML.search(testString)) return false;
	}
	return true;
}

doesCredentialContainerContain = function(testStrings) {
	return doesContainerContain("Remove_Credential_Container", testStrings);
}

doesMessageContainerContain = function(testStrings) {
	return doesContainerContain("PopupWindow_MessageDiv", testStrings);
}

doesSuccessContainerContain = function(testStrings) {
	return doesContainerContain("PopupWindow_SuccessDiv", testStrings);
}

doesErrorContainerContain = function(testStrings) {
	return doesContainerContain("PopupWindow_ErrorDiv", testStrings);
}

doesTitleContainerContain = function(testStrings) {
	return doesContainerContain("PopupWindow_ErrorDiv", testStrings);
}

doesMeContainerContain = function(testStrings) {
	return doesContainerContain("me_Msg", testStrings);
}

assert_IsPopupShown = function( assert ) { assert.ok(isPopupShown(), "popup div should be shown"); }
assert_IsPopupHidden = function( assert ) { assert.ok(isPopupHidden(), "popup div should be hidden"); }

callbackForAJAXtest = function(status,text,xml) {
	pageScript.callbackArgs = {
		status: status,
		text: text,
		xml: xml
		}
}

makeResponseDataForAJAXtest = function () {
	pageScript.status = 201;
	pageScript.text   = "szia";
	pageScript.xml    = xmlFor("<xml>hello</xml>");
}

var test=
	{
		win: {
			XMLHttpRequest: testXMLHttpRequestObject,
			location: window.location
			},
		debug: true
	}

console.log("runnning tests");

QUnit.jUnitReport = function(report) {
	console.log("writing report");
    document.getElementById("qunit-xml").innerHTML = report.xml;
    console.log(report.xml);
};

QUnit.module( "qeryStringFunc" ); 
QUnit.test( "should return an array of query strings contained in url", function( assert ) {
	var loc = { location: { search: "?something=y&otherthing=q&something=x&something=z" } } 
	var data={}
	data["something"]=["y","x","z"];
	data["otherthing"]="q";

	var qs = QueryStringFunc( loc );
	
	assert.equal(JSON.stringify(qs),JSON.stringify(data), "the arrays should equal" );
})


// AJAX functionalities

QUnit.module( "AJAX" ); 
QUnit.test( "ajaxbase() should return with a xmlhttp object - IE style httpRequest", function( assert ) {
		// Initializing test	
	pageScript = new PageScript(test)
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
	var _uribase = uribase;
	uribase = "base.uri.com";
		// calling the unit		
	pageScript.ajaxpost( testUrl, {data: "hello", name: "world"}, callbackForAJAXtest );
		// asserts 
	assert.ok(( pageScript.uri == uribase + testUrl &&
				pageScript.method == "POST" &&
				pageScript.async === true),
				"xmlhttp.open should be called with method='POST', url and async=true");
	assert.ok(( pageScript.header_name == "Content-type" && 
				pageScript.header_value == "application/x-www-form-urlencoded" ),
				"xmlhttp.setRequestHeader() should be called with data" );
	assert.equal( pageScript.data, "data=hello&name=world", "xmlhttp.send should be called with a message in its argument" );
	assert.equal( pageScript.callback.toString(), callbackForAJAXtest.toString(), "xmlhttp object should have the callback" );
		// cleaning
	uribase = _uribase;
});

QUnit.test( "ajaxget() can be mocked", function( assert ) {
		// Initializing the test		
	pageScript = new PageScript(test)
	var testUrl = "/my_url";
	var _uribase = uribase;
	uribase = "base.uri.com";
		// calling the unit		
	pageScript.ajaxget( testUrl, callbackForAJAXtest );
		// asserts 
	assert.ok(( pageScript.uri == uribase + testUrl &&
				pageScript.method == "GET" &&
				pageScript.async === true ),
				"xmlhttp.open should be called with method='GET', url and async=true");
	assert.notOk( pageScript.data, "xmlhttp.open should be called without args" );
	assert.equal( pageScript.callback.toString(), callbackForAJAXtest.toString(), "xmlhttp object should have the callback" );
		// cleaning
	uribase = _uribase;
});


// msg=processErrors(data={})

QUnit.module( "processErrors()" ); 
QUnit.test( "message is returned in message property", function( assert ) {
		// Initializing the test		
	pageScript = new PageScript(test);
	var testData = { message: "hello world" };
	var testMessage = "<p>message</p><p>hello world</p>";
	var testTitle = "Szerverüzenet";
		// calling the unit		
	var retVal = pageScript.processErrors( testData );
		// asserts 
	assert.equal( retVal.message, testMessage, "the 'message' property of the returned object gets its value" );
	assert.equal( retVal.title, testTitle, "the 'title' property of the returned object gets its value" );
});

QUnit.test( "errors is returned in error property", function( assert ) {
		// Initializing the test	
	pageScript = new PageScript(test);
	var testData  = { errors: ["hello world"] };
	var testError = "<ul><li>hello world</li></ul>";
	var testTitle = "Hibaüzenet";
		// calling the unit		
	var retVal = pageScript.processErrors( testData );
		// asserts 	
	assert.equal( retVal.error, testError, "the 'error' property of the returned object should get its value");
	assert.equal( retVal.title, testTitle, "the 'title' property of the returned object should get its value");	
});

QUnit.test( "assurances, email and userid are returned in success property", function( assert ) {
		// Initializing the test	
	pageScript = new PageScript(test)
	var testData = {
                'assurances': {
                        'test': '',
                        'foo': ''
                },
                'email': 'my@email.com',
                'userid': 'theuserid'
        };
	var testSuccess = "<p><b>e-mail cím:</b> my@email.com</p><p><b>felhasználó azonosító:</b> theuserid</p><p><b>hash:</b></p><pre>undefined</pre><p><b>tanusítványok:</b></p><ul><li>test</li><li>foo</li></ul><p><b>hitelesítési módok:</b></p><ul></ul>"
	var testTitle = "A felhasználó adatai";
		// calling the unit		
	var retVal = pageScript.processErrors( testData );
		// asserts 
	assert.equal( retVal.success, testSuccess, "the 'success' property of the returned object should get its value" );	
	assert.equal( retVal.title, testTitle, "the 'title' property of the returned object should get its value" );	
});


// displayMsg(msg={})

QUnit.module( "displaying and closing modal" ); 
QUnit.test( "the modal div should be able to appear", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	hidePopup();
	var testData = { title: "hello world" }
		// calling the unit	
	pageScript.displayMsg( testData );
		// asserts 
	assert_IsPopupShown( assert );
});

QUnit.test( "the modal div shouldn't be shown if its argument contains no data", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	hidePopup();
	var testData = { }
		// calling the unit	
	pageScript.displayMsg( testData );
		// asserts 
	assert_IsPopupHidden( assert );
});

QUnit.test( "with displayMsg() the text comes in the input data should be shown in their dedicated div element", function( assert ) {
	pageScript = new PageScript(test)
		// Initializing the test
	var testData = { 
		message: "hello world",
		error: "hello world",
		success: "hello world",
		title: "hello world"
		}
	var message_div_content="<p class=\"message\">hello world</p>"
	var error_div_content="<p class=\"warning\">hello world</p>"
	var success_div_content="<p class=\"success\">hello world</p>"
	var title_div_content="<h2>hello world</h2>"
		// calling the unit		
	pageScript.displayMsg( testData )
		// asserts 	
	assert.ok( doesMessageContainerContain( message_div_content ),
		"string in message property should be shown in the PopupWindow_MessageDiv element");
	assert.ok( doesErrorContainerContain( error_div_content),
		"string in error property should be shown in the PopupWindow_ErrorDiv element");	
	assert.ok( doesSuccessContainerContain( success_div_content ),
		"string in success property should be shown in the PopupWindow_SuccessDiv element");	
	assert.ok(document.getElementById("PopupWindow_TitleDiv").innerHTML, title_div_content, "string in title property should be shown in the PopupWindow_TitleDiv element");		
		// cleaning
	hidePopup();
});

QUnit.test( "with closePopup() the modal div should hide, erase its child divs and the callback function should be callable", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	pageScript.assert = assert
	var callback = function () { pageScript.isPopupCallbackCalled = true }
	document.getElementById("PopupWindow_TitleDiv").innerHTML='valami'
	document.getElementById("PopupWindow_SuccessDiv").innerHTML='valami'
	document.getElementById("PopupWindow_ErrorDiv").innerHTML='valami'
	document.getElementById("PopupWindow_MessageDiv").innerHTML='valami'
		// calling the unit	
	pageScript.closePopup( callback )
		// asserts 
	assert_IsPopupHidden( assert )
	assert.ok( pageScript.isPopupCallbackCalled, "callback should called" )
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "", "the 'PopupWindow_TitleDiv' should be empty");
	assert.equal(document.getElementById("PopupWindow_SuccessDiv").innerHTML, "", "the 'PopupWindow_SuccessDiv' should be empty");
	assert.equal(document.getElementById("PopupWindow_MessageDiv").innerHTML, "", "the 'PopupWindow_MessageDiv' should be empty");
	assert.equal(document.getElementById("PopupWindow_ErrorDiv").innerHTML, "", "the 'PopupWindow_ErrorDiv' should be empty");
});

QUnit.test( "the modal div should be hideable with close button click", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData = { title: "hello world" }
	pageScript.displayMsg( testData );
		// calling the unit	
	document.getElementById("PopupWindow_CloseButton").onclick();	
		// asserts 
	assert_IsPopupHidden( assert );
});

QUnit.test( "the callback function should be injected into the close button onclick function as argument", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData={ 
			title: "hello world", 
			callback: function() { pageScript.isPupopCloseButtonClickCallbackCalled = true } 
		}
	pageScript.displayMsg( testData )
		// calling the unit		
	document.getElementById("PopupWindow_CloseButton").onclick()
		// asserts 
	assert.ok( pageScript.isPupopCloseButtonClickCallbackCalled,
		"the function in onclick property should get the function in msg.callback as argument")
});

QUnit.test( "the onclick function shouldn't get any argumentum if msg.callback is missing or empty", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData={ title: "hello world" }
	pageScript.displayMsg( testData )
		// calling the unit	
	document.getElementById("PopupWindow_CloseButton").onclick()
		// asserts 
	assert.equal( pageScript.popupCallback.toString(), "", "the onclick function shouldn't get any argumentum")
});


// parseUserdata( userdata_object )

QUnit.module( "parseUserdata()" ); 
QUnit.test( "should parse the userdata contained an object to html", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var theUserId    = "theuserid"
	var theUserEmail = "my@email.com"
	var theDataObject = {
							"userid": theUserId,
						"assurances": {"test": "", "foo": ""},
							 "email": theUserEmail 
						}
		// calling the unit		
	var userData = pageScript.parseUserdata(theDataObject)
		// asserts 
	assert.ok( userData.search( theUserId ), "the output should contain the userid" )
	assert.ok( userData.search( theUserEmail ), "the output should contain the email address" )
});


// myCallback( htmlstatus, JSON_string )

QUnit.module( "myCallback()" ); 
QUnit.test( "shouldn't redirect if the status isn't equal 200", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	var testStatus = 201;
	var oldLocation = win.location;
	var oldQueryString = QueryString;
	QueryString.next = "newlocation";
		// calling the unit	
	pageScript.myCallback( testStatus, testData )
		// asserts 
	assert.equal( win.location, oldLocation, "If the status!=200 the window.location shouldn't get new value");	
		//cleaning
	hidePopup()
	win.location = oldLocation
	QueryString = oldQueryString
});

QUnit.test( "shouldn't redirect if the status is 200 but no next key or value is given in query string", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	var testStatus = 200;
	var oldQueryString = QueryString;
	var oldLocation = win.location;
	delete QueryString.next;
		// calling the unit	
	pageScript.myCallback( testStatus, testData )
		// asserts 
	assert.equal( win.location, oldLocation, "if no next is given the window.location shouldn't get new value");	
		//cleaning
	hidePopup()
	win.location = oldLocation
	QueryString = oldQueryString
});

QUnit.test( "should redirect with 'next' query var comes in url if status=200", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	var testStatus = 200;
	var oldQueryString = QueryString;
	var oldLocation = win.location;
	QueryString.next = "newlocation";
		// calling the unit		
	pageScript.myCallback( testStatus, testData )
		// asserts 
	assert.equal(win.location, "newlocation", "with status 200 the window.location should get the new location");	
		//cleaning
	hidePopup()
	win.location = oldLocation
	QueryString = oldQueryString
});

QUnit.test( "should display the processed data through processErrors() and displayMsg(), popop callback should have the get_me()", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	testData = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
		// calling the unit	
	pageScript.myCallback( 200, testData )
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesSuccessContainerContain("my@email.com"), "the data should be shown in popup window");	
	assert.equal( pageScript.msg.callback, pageScript.get_me.toString() , "the function in PopupWindow_CloseButton onclick property should get the function 'get_me' as argument'")
		//cleaning
	hidePopup();
});


// get_me() calls /v1/users/me

QUnit.module( "get_me()" ); 
QUnit.test( "should call '/v1/users/me' trough AJAX", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testUri = "/v1/users/me";
	var testMethod = "GET"
		// calling the unit	
	pageScript.get_me();
		// asserts
	assert.equal(pageScript.uri, testUri, "the URI should be '/v1/users/me'");
	assert.equal(pageScript.method, testMethod, "the method should be GET");
	assert.equal(pageScript.callback.toString(), pageScript.initCallback.toString(), "callback function should be the 'initCallback'");
});


// initCallback( htmlstatus, JSON )

QUnit.module( "initCallback()" ); 
QUnit.test( "should set visibility of the menutabs according the user rights - no autorization", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testData = '{"errors": ["no authorization"]}'
	var testStatus = 400
		// calling the unit	
	pageScript.initCallback( testStatus, testData )
		// asserts	
	assert.ok((	!isLoginButtonHidden() && 
				!isRegistrationButtonHidden() &&
				isAssurerButtonHidden() &&
				isAccountButtonHidden() ),
			"user specific tabs should be hidden and login, registration tabs should be shown if no user logged in" );
	assert.ok( isPopupHidden(), "popup window should be still hidden if 'no authorization'");
})

QUnit.test( "should set the visibility of the menutabs according the user rights - Any other message", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testData = '{"errors": ["any other error"]}';
	var testStatus = 400;
		// calling the unit	
	pageScript.initCallback( testStatus, testData );
		// asserts
	assert.ok((	!isLoginButtonHidden() &&
				!isRegistrationButtonHidden() &&
				isAssurerButtonHidden() &&
				isAccountButtonHidden() ),
			"user specific tabs should be hidden and login, registration tabs should be shown if no user logged in" );
	assert.ok( isPopupShown(), "popup window should be shown if any other message comes in the AJAX response");
		//cleaning
	hidePopup();
})

QUnit.test( "should set the visibility of the menu tabs according the user rights - user without 'assurer' assurance and credentials", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testData = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	var testStatus = 200;
		// calling the unit	
	pageScript.initCallback( testStatus, testData );
		// asserts
	assert.ok((	isLoginButtonHidden() &&
				isRegistrationButtonHidden() &&
				!isAccountButtonHidden() ),
			"Account tab should be shown")
	assert.ok( isAssurerButtonHidden(), "assurer tab should be hidden if the user don't has 'assurer' assurance")
	assert.ok( isCredentialContainerEmpty(),"if no credential nothing should be shown in div of credentials")
	assert.equal( document.getElementById("AddSslCredentialForm_email_input").value,"my@email.com",
		"AddSslCredentialForm_email_input should contain the email" );
	assert.equal( document.getElementById("PasswordResetInitiateForm_email_input").value,"my@email.com",
		"PasswordResetInitiateForm_email_input should contain the email" );
	assert_IsPopupHidden( assert );
})

QUnit.test( "hides account and assurer menutabs and shows login and registration if the html status not 200", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testData = '{"userid":"theuserid","assurances":{"assurer":{"date":""},"foo":""},"credentials":[{"credentialType":"facebook","identifier":"828377612368497"}],"email":"my@email.com"}';
	var testStatus = 200;
		// calling the unit		
	pageScript.initCallback( testStatus, testData );
		// asserts	
	assert.notOk((	!isLoginButtonHidden() &&
					!isRegistrationButtonHidden() &&
					isAccountButtonHidden() ),
				"account tab should be shown and login, registration tabs should be hidden" );
	assert.ok( !isAssurerButtonHidden(), "assurer tab should be shown if the user has 'assurer' assurance" );
	assert.ok( doesCredentialContainerContain( ["facebook", "828377612368497"] ),"credentials should be shown in credential container" );
	assert_IsPopupHidden( assert );
});


// passwordReset("formName")

QUnit.module( "passwordReset()" ); 
QUnit.test( "passwordReset calls /v1/password_reset with secret and password", function( assert ) {
		// Initializing the test
	document.getElementById("PasswordResetForm_OnLoginTab_secret_input").value = "thesecret";
	document.getElementById("PasswordResetForm_OnLoginTab_password_input").value = "thepassword";
	pageScript = new PageScript(test);
	var testUri = "/v1/password_reset";
	var testMethod = "POST";
	var testData = "secret=thesecret&password=thepassword";
	var testForm = "PasswordResetForm_OnLoginTab";
		// calling the unit	
	pageScript.passwordReset( testForm );
		// asserts		
	assert.equal(pageScript.uri, testUri, "uri should be '/v1/password_reset'" );
	assert.equal(pageScript.data, testData, "data to send should contain secret and password" );
	assert.equal(pageScript.method, testMethod, "method should be 'POST'" );
	assert.equal(pageScript.callback.toString(), pageScript.myCallback.toString(), "callback should be myCalback()" );
});


// InitiatePasswordReset(formName)

QUnit.module( "InitiatePasswordReset()" ); 
QUnit.test( "calls AJAX with method 'GET' on uri /v1/users/'email'/passwordreset", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testForm = "PasswordResetInitiateForm_OnLoginTab";
	var testUri = "/v1/users/my@email.com/passwordreset";
	var testMethod = "GET";
	document.getElementById( testForm + "_email_input" ).value = "my@email.com";
		// calling the unit	
	pageScript.InitiatePasswordReset( testForm );
		// asserts		
	assert.equal( pageScript.uri, testUri, "uri should be '/v1/password_reset/my@email.com/passwordreset'" );
	assert.equal( pageScript.method, testMethod, "method should be 'GET'" );
	assert.equal( pageScript.callback.toString(), pageScript.myCallback.toString(), "callback should be myCalback()" );
});


// login methods
QUnit.module( "login methods" ); 

// password login
QUnit.test( "login() calls /login with 'password' as credential type, username and password", function( assert ) {
		// Initializing the test
	document.getElementById("LoginForm_username_input").value = "theuser"
	document.getElementById("LoginForm_password_input").value = "thepassword"
	pageScript = new PageScript(test)
	var testUri = "/login";
	var testMethod = "POST";
	var testData = "credentialType=password&identifier=theuser&secret=thepassword";
		// calling the unit	
	pageScript.login();
		// asserts		
	assert.equal(pageScript.uri, testUri, "uri should be '/login'");
	assert.equal(pageScript.data, testData, "data should contain the credential type, the username and the password");
	assert.equal(pageScript.method, testMethod, "method should be POST");
	assert.equal( pageScript.callback.toString(), pageScript.myCallback.toString(), "callback should be myCalback()" );
});

QUnit.test( "error message should be shown if the input fields are empty, AJAX shouldn't be called", function( assert ) {
		// Initializing the test
	document.getElementById("LoginForm_username_input").value = "";
	document.getElementById("LoginForm_password_input").value = "";
	pageScript = new PageScript(test);
		// calling the unit	
	pageScript.login();
		// asserts	
	assert_IsPopupShown(assert);
	assert.ok( doesErrorContainerContain( ['felhasználónév','jelszó'] ), "the error container should contain the error messages" );
	assert.notOk( pageScript.callback, "Ajax shouldn't be called" );
		// cleaning
	hidePopup();
});

// sslLogin()
QUnit.test( "sslLogin() should redirect to the SSL_LOGIN_BASE_URL uri", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var oldLocation = win.location
	var oldQueryString = QueryString;
	win.location="https://valami.com/base"
	QueryString.uris={SSL_LOGIN_BASE_URL: "SSL_base", BASE_URL:"base"}
	var testURL="https://valami.com/SSL_base"
		// calling the unit
	pageScript.sslLogin();
		// asserts
	assert.equal( win.location, testURL, "should redirected to SSL_LOGIN_BASE_URL" );
		//cleaning
	win.location = oldLocation
	QueryString = oldQueryString 		
});

// login_with_facebook
QUnit.test( "login_with_facebook calls /login with facebook as credential type, userid and access token", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testUri = "/login";
	var testMethod = "POST";
	var testData = "credentialType=facebook&identifier=fbid&secret=accessToken";
		// calling the unit	
	pageScript.login_with_facebook( "fbid", "accessToken" );
		// asserts	
	assert.equal(pageScript.uri, testUri, "uri should be '/login'");
	assert.equal(pageScript.data, testData, "data should contain 'facebook' as credential type, 'fbid' as userid, and 'accessToken' as secret");
	assert.equal(pageScript.method, testMethod, "method should be POST");
	assert.equal( pageScript.callback.toString(), pageScript.myCallback.toString(), "callback should be myCalback()" );
});

// GoogleLogin()
QUnit.test( "[ Must be implemented!! ] Should logging in with google account", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
		// calling unit
	pageScript.GoogleLogin()
		// asserts
	assert_IsPopupShown(assert);
		// cleaning
	hidePopup();
})

// TwitterLogin()
QUnit.test( "[ Must be implemented!! ] Should logging in with twitter account", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
		// calling unit
	pageScript.TwitterLogin()
		// asserts
	assert_IsPopupShown(assert);
		// cleaning
	hidePopup();
})


// Assurance functionalities
QUnit.module( "Assurance functionalities" ); 

// check data of an user selected by Email
QUnit.test( "byEmail() should request the server for the data of the user selected by Email", function( assert ) {
		// Initializing the test
	var oldEmail = document.getElementById("ByEmailForm_email_input").value
	document.getElementById("ByEmailForm_email_input").value = "email@address.com";
	pageScript = new PageScript(test);
	var checkUri = "/v1/user_by_email/email%40address.com"
	var checkMethod = "GET";
	var checkCallback = pageScript.myCallback;
		// calling the unit	
	pageScript.byEmail();
		// asserts		
	assert.equal( pageScript.uri, checkUri, "uri should be /v1/user_by_email/email%40address.com");
	assert.equal( pageScript.method, checkMethod, "the method should be GET");
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be myCallback()" );
		//cleaning
	document.getElementById("ByEmailForm_email_input").value = oldEmail;
});

// addAssurance
QUnit.test( "addAssurance() should call '/v1/add_assurance' with digest, assurance and email", function( assert ) {
		// Initializing the test
	var oldDigest = document.getElementById("AddAssuranceForm_digest_input").value;
	var oldAssurance = document.getElementById("AddAssuranceForm_assurance_input").value;
	var oldEmail = document.getElementById("AddAssuranceForm_email_input").value;
	document.getElementById("AddAssuranceForm_digest_input").value = "digest";
	document.getElementById("AddAssuranceForm_assurance_input").value = "assurance";
	document.getElementById("AddAssuranceForm_email_input").value = "email@e.mail";
	test.win.document = {cookie:"csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"};
	pageScript = new PageScript(test);
	var checkUri = "/v1/add_assurance";
	var checkData = "digest=digest&assurance=assurance&email=email%40e.mail&csrf_token=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef";
	var checkMethod = "POST";
	var checkCallback = pageScript.myCallback;
		// calling the unit	
	pageScript.addAssurance();
		// asserts	
	assert.equal( pageScript.uri, checkUri, "uri should be '/v1/add_assurance'" );
	assert.equal( pageScript.data, checkData, "Ajax should get the stringified data" );
	assert.equal( pageScript.method, checkMethod, "method should be 'POST'" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be the myCallback()" );
		// cleaning
	document.getElementById("AddAssuranceForm_digest_input").value = oldDigest;
	document.getElementById("AddAssuranceForm_assurance_input").value = oldAssurance;
	document.getElementById("AddAssuranceForm_email_input").value = oldEmail;
});

// logout functionalities
QUnit.module( "logout" ); 

// logout()
QUnit.test( "logout() should call AJAX with method 'GET' on uri /logout and callback should be logoutCallback()", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testUri = "/logout";
	var testMethod = "GET";
	var checkCallback = pageScript.logoutCallback;	
		// calling the unit	
	pageScript.logout();
		// asserts		
	assert.equal(pageScript.uri, testUri, "uri should be '/logout'" );
	assert.equal(pageScript.method, testMethod, "method should be 'GET'" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be logoutCallback()" );
});

// logoutCallback()
QUnit.test( "logoutCallback() should display the response comes from the server", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testStatus = 200;
	var testText = '{"message": "logged out"}';
	var checkCallback = pageScript.doLoadHome;
	var checkData = ['message','logged out'];
		// calling the unit		
	pageScript.logoutCallback( testStatus, testText);
		// asserts		
	assert_IsPopupShown( assert );
	assert.ok( doesMessageContainerContain( checkData ), "the message div should contain the message of the server" );
	assert.equal( pageScript.msgCallback.toString(), checkCallback.toString(), "the callback function in the close button onclick should do redirect to home")
		// cleaning
	hidePopup();
});

// doLoadHome()
QUnit.test( "doLoadHome() should redirect to the location contained in the QueryString.uris.START_URL", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var oldQueryString = QueryString;
	var oldLocation = win.location;
	QueryString.uris = {START_URL: "newlocation"};
		// calling the unit		
	pageScript.doLoadHome();
		// asserts 
	assert.equal( win.location, "newlocation", "windows.location should get the url contained in the QS" );	
		//cleaning
	win.location = oldLocation
	QueryString = oldQueryString
});


// uriCallback()
QUnit.module( "uriCallback()" ); 

QUnit.test( "should fill the 'QeryString.uris' array with the datas have coming from the URi service of server", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var oldLocation = win.location
	var testText =	'{"BASE_URL": "https://sso.edemokraciagep.org",' +
					'"PASSWORD_RESET_FORM_URL": "https://sso.edemokraciagep.org/static/login.html",' +
					'"SSL_LOGIN_BASE_URL": "https://sso.edemokraciagep.org:8080",' +
					'"SSL_LOGOUT_URL": "https://sso.edemokraciagep.org/ssl_logout/",' +
					'"START_URL": "https://sso.edemokraciagep.org/static/login.html"}'
	var testStatus = 200;
	var oldQueryString = QueryString;
		// calling the unit
	pageScript.uriCallback( testStatus, testText )
		// asserts
	assert.equal( JSON.stringify(QueryString.uris), JSON.stringify(JSON.parse(testText)),"QueryString.uris should contain the data" );	
		//cleaning
	win.location = oldLocation
	QueryString = oldQueryString 		
});

QUnit.test( "should display the errors in error div if the server sent any error", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var oldLocation = win.location
	var testJSONtext =	'{"errors": ["error message"]}';
	var testStatus = 400;
	var oldQueryString = QueryString;
	var checkString = "error message"
	delete QueryString.uris;
		// calling the unit
	pageScript.uriCallback( testStatus, testJSONtext )
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesErrorContainerContain( checkString ),"the error container should contain the error message" );
	assert.notOk( QueryString.uris, "the QueryString.uris should be unchanged" );
		//cleaning
	hidePopup();
	win.location = oldLocation
	QueryString = oldQueryString 		
});


// register
QUnit.module( "registering" ); 

// registering with username and password
QUnit.test( "register() calls /v1/register with all the data needed for registration", function( assert ) {
		// Initializing the test
	var oldPassword = document.getElementById("RegistrationForm_credentialType_input").value;
	var oldIdentifier = document.getElementById("RegistrationForm_identifier_input").value;
	var oldSecret = document.getElementById("RegistrationForm_secret_input").value;
	var oldEmail = document.getElementById("RegistrationForm_email_input").value;
	var oldDigest = document.getElementById("RegistrationForm_digest_input").value;
	document.getElementById("RegistrationForm_credentialType_input").value = "password";
	document.getElementById("RegistrationForm_identifier_input").value = "identifier";
	document.getElementById("RegistrationForm_secret_input").value = "secret";
	document.getElementById("RegistrationForm_email_input").value = "email@mail.com";
	document.getElementById("RegistrationForm_digest_input").value = "thedigest";
	var checkUri = "/v1/register";
	var checkData = "credentialType=password&identifier=identifier&secret=secret&email=email%40mail.com&digest=thedigest";
	var checkMethod = "POST";
	var checkCallback = pageScript.myCallback;
	pageScript = new PageScript(test)
		// calling the unit	
	pageScript.register()
		// asserts	
	assert.equal(pageScript.uri, checkUri, "uri should be '/v1/register'" );
	assert.equal(pageScript.data, checkData, "AJAX should get the stringified data" );
	assert.equal(pageScript.method, checkMethod, "the method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be myCallback()" );
		// cleaning
	document.getElementById("RegistrationForm_credentialType_input").value = oldPassword;
	document.getElementById("RegistrationForm_identifier_input").value = oldIdentifier;
	document.getElementById("RegistrationForm_secret_input").value = oldSecret;
	document.getElementById("RegistrationForm_email_input").value = oldEmail;
	document.getElementById("RegistrationForm_digest_input").value = oldDigest;
});

// register with facebook
QUnit.test( "facebookregister_with_facebook() calls /v1/register with all the data needed for facebook registration", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var checkUri = "/v1/register";
	var checkData = "credentialType=facebook&identifier=userId&secret=accessToken&email=email%40example.com";
	var checkMethod = "POST";
	var checkCallback = pageScript.myCallback;
		// calling unit
	pageScript.register_with_facebook("userId", "accessToken", "email@example.com");
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be '/v1/register'" );
	assert.equal( pageScript.data, checkData, "AJAX should get the stringified data" );
	assert.equal( pageScript.method, checkMethod, "the method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be myCallback()" );
});

// register with google
QUnit.test( "[ Must be implemented!! ] Should registering with google account", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
		// calling unit
	pageScript.GoogleRegister()
		// asserts
	assert_IsPopupShown(assert);
		// cleaning
	hidePopup();
})


// getCookie

QUnit.module( "getCookie()" ); 
QUnit.test( "getCookie extracts the named cookie", function( assert ) {
		// Initializing the test
	test.win.document = {cookie:"csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"}
	pageScript = new PageScript(test)
	var checkData = "64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"
		// calling unit
	var cookie = pageScript.getCookie('csrf')
		// asserts
	assert.equal( cookie, checkData, "the cookie content should be equal with the stored one" );
});

QUnit.test( "getCookie should return empty if there no named cookie", function( assert ) {
		// Initializing the test
	test.win.document = {cookie: ""}
	pageScript = new PageScript(test)
	var checkData = ""
		// calling unit
	var cookie = pageScript.getCookie('csrf')
		// asserts
	assert.equal( cookie, checkData, "the cookie should return empty" );
});


// InitiateResendRegistrationEmail

QUnit.module( "InitiateResendRegistrationEmail()" ); 
QUnit.test( "[ Must be implemented!! ] User should be able to initiate resending the registration email", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
		// calling unit
	pageScript.InitiateResendRegistrationEmail()
		// asserts
	assert_IsPopupShown(assert);
		// cleaning
	hidePopup();
})

// Hash functions
QUnit.module( "Hash functions" ); 

// digestGetter
QUnit.test( "digestGetter()getDigest should call anchor for digest", function( assert ) {
		// Initializing the test
	var testForm = "AddAssuranceForm";
	var oldPredigest = document.getElementById( testForm + "_predigest_input").value;
	var oldDigest = document.getElementById( testForm + "_digest_input").value;
	document.getElementById( testForm + "_predigest_input").value = "xxpredigestxx";
	pageScript = new PageScript(test)
	var checkUri = "https://anchor.edemokraciagep.org/anchor";
	var checkData = "<id>xxpredigestxx</id>";
	var checkMethod = "POST";
		// calling unit	
	pageScript.digestGetter( testForm ).getDigest();
	var checkCallback = pageScript.idCallback;   // idCallback() is defined in digestGetter()
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be 'https://anchor.edemokraciagep.org/anchor'" );
	assert.equal( pageScript.data, checkData, "AJAX should get the stringified data" );
	assert.equal( pageScript.method, checkMethod, "the method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be the idCallback()" );
		// cleaning
	document.getElementById( testForm + "_predigest_input").value = oldPredigest;
});

QUnit.test( "digestGetter()getDigest should display an error message if predigest field doesn't contain any value", function( assert ) {
		// Initializing the test
	var testForm = "AddAssuranceForm";
	var oldPredigest = document.getElementById( testForm + "_predigest_input").value;
	document.getElementById( testForm + "_predigest_input").value = "";
	pageScript = new PageScript(test)
	var checkString = "A személyi szám nincs megadva";
		// calling unit	
	pageScript.digestGetter( testForm ).getDigest();
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesErrorContainerContain( checkString ), "the error container should contain the error message" );
		// cleaning
	document.getElementById( testForm + "_predigest_input").value = oldPredigest;
	hidePopup();
});

QUnit.test( "digestGetter().idCallback() should display the error message sent by the server", function( assert ) {
		// Initializing the test
	var testForm = "AddAssuranceForm";
	pageScript = new PageScript(test)
	var testStatus = 400;
	var testText = 'Some message from the server';
		// calling unit	
	pageScript.digestGetter( testForm ).idCallback( testStatus, testText, "" );
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesErrorContainerContain( testText ), "the error container should contain the error message" );
		// cleaning
	hidePopup();
});

QUnit.test( "digestGetter().idCallback() should put the digest into the digest input field, and display the success message", function( assert ) {
		// Initializing the test
	var testForm = "AddAssuranceForm";
	var oldPredigest = document.getElementById( testForm + "_predigest_input").value;
	var oldDigest = document.getElementById( testForm + "_digest_input").value;
	document.getElementById( testForm + "_predigest_input").value = "xxpredigestxx";
	document.getElementById( testForm + "_digest_input").value = "";
	pageScript = new PageScript(test)
	var testStatus = 200;
	var testText = '<hash>thehash</hash>';
	var testXML = xmlFor( testText );
	var checkMessage = "A titkosítás sikeres";
		// calling unit	
	pageScript.digestGetter( testForm ).idCallback( testStatus, testText, testXML );
		// asserts
	assert.equal( document.getElementById( testForm + "_digest_input" ).value, "thehash", "the digest input field should be contain the hash" )
	assert.equal( document.getElementById( testForm + "_predigest_input" ).value, "", "the predigest input should be cleared")
	assert_IsPopupShown( assert );
	assert.ok( doesSuccessContainerContain( checkMessage ), "the error container should contain the error message" );
		// cleaning
	document.getElementById( testForm + "_predigest_input").value = oldPredigest;
	document.getElementById( testForm + "_digest_input").value = oldDigest;
	hidePopup();
});


// changeHash
QUnit.module( "changing hash" ); 
QUnit.test( "changeHash() should call '/v1/users/me/update_hash' to initiate changing the hash", function( assert ) {
		// Initializing the test
	var testForm = "ChangeHashForm";
	var oldDigest = document.getElementById( testForm + "_digest_input").value;
	document.getElementById( testForm + "_digest_input").value = "this is the hash";
	test.win.document = {cookie:"csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"};
	pageScript = new PageScript(test)
	var checkUri = "/v1/users/me/update_hash";
	var checkData = "digest=this%20is%20the%20hash&csrf_token=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef";
	var checkMethod = "POST";
	var checkCallback = pageScript.hashCallback;
		// calling unit	
	pageScript.changeHash();
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be 'https://anchor.edemokraciagep.org/anchor'" );
	assert.equal( pageScript.data, checkData, "AJAX should get the stringified data" );
	assert.equal( pageScript.method, checkMethod, "the method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be the hashCallback()" );
		// cleaning
	document.getElementById( testForm + "_digest_input").value = oldDigest;
});

// hashCallback
QUnit.test( "hashCallback() should display the error message sent by the server", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testStatus = 400;
	var testJSONtext = '{"errors": ["error message"]}';
	var checkString = "error message"
		// calling unit	
	pageScript.hashCallback( testStatus, testJSONtext );
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesErrorContainerContain( checkString ), "the error container should contain the error message" );
		// cleaning
	hidePopup();
});

QUnit.test( "if the server's response is 200, hashCallback() should display the success message, and close button callback should be 'refreshMe' ", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testStatus = 200;
	var testJSONtext = '{"userid":"theuserid","assurances":{"assurer":{"date":""},"foo":""},"credentials":[{"credentialType":"facebook","identifier":"828377612368497"}],"email":"my@email.com"}';
	var checkMessage = "A titkos kód frissítése sikeresen megtörtént";
	var checkCalback = pageScript.refreshMe;
		// calling unit	
	pageScript.hashCallback( testStatus, testJSONtext );
		// asserts
	assert.ok( doesMeContainerContain( checkMessage ), "the error container should contain the error message" );
		// cleaning
});

// refreshing the user data container
QUnit.module( "refreshMe" ); 

// refreshMe()
QUnit.test( "refreshMe() should call '/v1/users/me' trough AJAX for user's data", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test)
	var testUri = "/v1/users/me";
	var testMethod = "GET"
	var testCallback = pageScript.refreshCallback;
		// calling the unit	
	pageScript.refreshMe();
		// asserts
	assert.equal(pageScript.uri, testUri, "the URI should be '/v1/users/me'");
	assert.equal(pageScript.method, testMethod, "the method should be GET");
	assert.equal(pageScript.callback.toString(), testCallback.toString(), "callback function should be the 'refreshCallback'");
});

// refreshCallback()
QUnit.test( "if the server's response is 200, refreshCallback() should refresh the user data container", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	testStatus = 200;
	testJSONtext = '{"userid": "theuserid", "hash": "Ez pedig valami jó hosszú szám lesz", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	var checkMessage = "Ez pedig valami jó hosszú szám lesz";
		// calling unit	
	pageScript.refreshCallback( testStatus, testJSONtext );
		// asserts
	assert.ok( doesSuccessContainerContain( checkMessage ), "the error container should contain the error message" );
});

QUnit.test( "refreshCallback() should display the error message responsed by the server if the status is not equal 200", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	testStatus = 400;
	testJSONtext = '{"errors": ["error message"]}';
	var checkMessage = "error message";
		// calling unit	
	pageScript.refreshCallback( testStatus, testJSONtext );
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesSuccessContainerContain( checkMessage ), "the error container should contain the error message" );
		// cleaning
	hidePopup();
});


// changeEmailAddress

QUnit.module( "changeEmailAddress()" ); 
QUnit.test( "Error message should be displayed if the email field is empty", function( assert ) {
		// Initializing the test
	var oldEmail = document.getElementById("ChangeEmailAddressForm_email_input").value
	document.getElementById("ChangeEmailAddressForm_email_input").value = ""
	var checkMessage = "Nincs megadva érvényes e-mail cím"
	pageScript = new PageScript(test);
		// calling unit
	pageScript.changeEmailAddress()
		// asserts
	assert_IsPopupShown(assert);
	assert.ok( doesErrorContainerContain( checkMessage ), "the error container should contain the error message" );
		// cleaning
	document.getElementById("ChangeEmailAddressForm_email_input").value = oldEmail
	hidePopup();
})

QUnit.test( "[ Must be implemented!! ] User should be able to initiate resending the registration email", function( assert ) {
		// Initializing the test
	var oldEmail = document.getElementById("ChangeEmailAddressForm_email_input").value
	document.getElementById("ChangeEmailAddressForm_email_input").value = "test@example.org"
	pageScript = new PageScript(test);
		// calling unit
	pageScript.changeEmailAddress()
		// asserts
	assert_IsPopupShown(assert);
		// cleaning
	hidePopup();
})

// RemoveCredential

QUnit.module( "RemoveCredential()" ); 
QUnit.test( "RemoveCredential().doRemove should call '/v1/remove_credential' to initiate removing the credential", function( assert ) {
		// Initializing the test
	var testForm = "RemoveCredential_0";
	var oldDiv = document.getElementById("Remove_Credential_Container").innerHtml
	var testDiv = '<div id="RemoveCredential_0"><table class="content_"><tbody><tr>'+
				'<td width="25%"><p id="RemoveCredential_0_credentialType">facebook</p></td>'+
				'<td style="max-width: 100px;"><pre id="RemoveCredential_0_identifier">828377612368497</pre></td>'+
				'<td width="10%"><div><button class="button" type="button" id="RemoveCredential_0_button" onclick="javascript:pageScript.RemoveCredential('+
				"'RemoveCredential_0'"+
				').doRemove()">Törlöm</button></div></td></tr></tbody></table></div>';
	document.getElementById("Remove_Credential_Container").innerHtml=testDiv;
	test.win.document = {cookie:"csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"};
	pageScript = new PageScript(test)
	var checkUri = "/v1/remove_credential";
	var checkData = "csrf_token=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef&credentialType=facebook&identifier=828377612368497";
	var checkMethod = "POST";
	var checkCallback = pageScript.myCallback;
		// calling unit	
	pageScript.RemoveCredential(testForm).doRemove();
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be '/v1/remove_credential'" );
	assert.equal( pageScript.data, checkData, "AJAX should get the stringified data" );
	assert.equal( pageScript.method, checkMethod, "the method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be the myCallback()" );
		// cleaning
	document.getElementById("Remove_Credential_Container").innerHtml = oldDiv;
});

// addding credentials
QUnit.module( "addding credentials" ); 

// callback for adding credentials
QUnit.test( "credential callback should display error messages if they came from the server", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testJSONtext = '{"errors": ["no authorization"]}'
	var testStatus = 400;
	var checkData = "no authorization";
		// calling unit
	pageScript.addCredentialCallback( testStatus, testJSONtext );
		// asserts
	assert_IsPopupShown(assert);
	assert.ok( doesErrorContainerContain( checkData ), "the popup should contain the error message" );
		// cleaning
	hidePopup();
})

QUnit.test( "credential callback should display a succes messages and initiate to refresh the userdata container trough the close button's callback", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testJSONtext = '{"userid":"theuserid","assurances":{"assurer":{"date":""},"foo":""},"credentials":[{"credentialType":"facebook","identifier":"828377612368497"}],"email":"my@email.com"}';
	var testStatus = 200;
	var checkData = "Hitelesítési mód sikeresen hozzáadva";
	var checkCallback = pageScript.get_me
		// calling unit
	pageScript.addCredentialCallback( testStatus, testJSONtext );
		// asserts
	assert_IsPopupShown( assert );
	assert.ok( doesSuccessContainerContain( checkData ), "the popup should contain the success message" );
	assert.equal(pageScript.msgCallback.toString(), checkCallback.toString(), "close button should contain the callback to initiate refreshing the UI with the updated user data")
		// cleaning
	hidePopup();
})

// addCredential()
QUnit.test( "addCredential() should send a POST request trough AJAX and callback should be the addCredentialCalback()", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
	var testCredentialType= "the_credentialType";
	var testIdentifier = "the_identifier";
	var testSecret= "the_secret";
	var checkUri = "/v1/add_credential";
	var checkMethod = "POST";
	var checkData = "credentialType=the_credentialType&identifier=the_identifier&secret=the_secret";
	var checkCallback = pageScript.addCredentialCallback
		// calling unit
	pageScript.addCredential( testCredentialType, testIdentifier, testSecret );
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be '/v1/add_credential'" );
	assert.equal( pageScript.data, checkData, "data should contain the credential type, the identifier and the secret" );
	assert.equal( pageScript.method, checkMethod, "method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be addCredentialCallback()" );
})

// add password credential
QUnit.test( "should initiate an AJAX process to add a password credential with username and password comes from input fields", function( assert ) {
		// Initializing the test 
	var oldUser = document.getElementById("AddPasswordCredentialForm_username_input").value;
	var oldPassword = document.getElementById("AddPasswordCredentialForm_password_input").value;
	document.getElementById("AddPasswordCredentialForm_username_input").value = "the_UserName";
	document.getElementById("AddPasswordCredentialForm_password_input").value = "the_Password";
	pageScript = new PageScript(test);
	var checkUri = "/v1/add_credential";
	var checkMethod = "POST";
	var checkData = "credentialType=password&identifier=the_UserName&secret=the_Password";
	var checkCallback = pageScript.addCredentialCallback
		// calling unit
	pageScript.addPassowrdCredential();
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be '/v1/add_credential'" );
	assert.equal( pageScript.data, checkData, "data should contain the credential type, the identifier and the secret" );
	assert.equal( pageScript.method, checkMethod, "method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be addCredentialCallback()" );
		// clean
	document.getElementById("AddPasswordCredentialForm_username_input").value = oldUser;
	document.getElementById("AddPasswordCredentialForm_password_input").value = oldPassword;
})

// add facebook credential
QUnit.test( "should initiate an AJAX process to add a facebook credential with fb_userid and fb_accessToken comes from fb", function( assert ) {
		// Initializing the test 
	pageScript = new PageScript(test);
	var testUserId = "the_fbUserID";
	var tesAccessToken = "the_accessToken"
	var checkUri = "/v1/add_credential";
	var checkMethod = "POST";
	var checkData = "credentialType=facebook&identifier=the_fbUserID&secret=the_accessToken";
	var checkCallback = pageScript.addCredentialCallback
		// calling unit
	pageScript.add_facebook_credential( testUserId, tesAccessToken );
		// asserts
	assert.equal( pageScript.uri, checkUri, "uri should be '/v1/add_credential'" );
	assert.equal( pageScript.data, checkData, "data should contain the credential type, the identifier and the secret" );
	assert.equal( pageScript.method, checkMethod, "method should be POST" );
	assert.equal( pageScript.callback.toString(), checkCallback.toString(), "callback should be addCredentialCallback()" );
})
QUnit.module( "add_facebook_credential()" ); 

// addGoogleCredential()
QUnit.test( "[ Must be implemented!! ] should initiate an AJAX process to add a google credential with google_userid and google_accessToken comes from google", function( assert ) {
		// Initializing the test
	pageScript = new PageScript(test);
		// calling unit
	pageScript.addGoogleCredential()
		// asserts
	assert_IsPopupShown(assert);
		// cleaning
	hidePopup();
})


// deRegister()

QUnit.module( "deRegister()" ); 


// menuHandler("menuName")

QUnit.module( "menuHandler()" ); 
QUnit.test( "menuHandler can hide and display the tabs", function( assert ) {
		// Initializing the test
	document.getElementById("login-menu").style.display="block";
	pageScript = new PageScript(test)
	pageScript.menuHandler("login").menuHide();
	assert.equal(document.getElementById("login-menu").style.display,"none","login menu should be hidden");
	pageScript.menuHandler("login").menuUnhide();
	assert.equal(document.getElementById("login-menu").style.display,"block","login menu should be shown");
	document.getElementById("login-menu").className="";
	document.getElementById("tab-content-login").style.display="none";
	pageScript.menuHandler("login").menuActivate();
	assert.equal(document.getElementById("login-menu").className,"active-menu","login menu should be activated");
	assert.equal(document.getElementById("tab-content-login").style.display,"block","login tab should be shows");
	pageScript.menuHandler("login").menuActivate();
	assert.equal(pageScript.activeButtonName,"login","the 'login' should be the active button");
	assert.equal(pageScript.activeButton.id,"login-menu","the 'login-menu' should be the active button id");
	assert.equal(pageScript.activeTab.id,"tab-content-login","the 'tab-content-login' should be the active tab id");
	pageScript.menuHandler("registration").menuActivate();
	assert.equal(document.getElementById("login-menu").className,"","login menu should be deactivated");
	assert.equal(document.getElementById("tab-content-login").style.display,"none","login tab should be hidden");
	pageScript.menuHandler("registration");
	assert.equal(pageScript.activeButtonName,"registration","the 'registration' should be the active button");
	assert.equal(pageScript.activeButton.id,"registration-menu","the 'registration-menu' should be the active button id");
	assert.equal(pageScript.activeTab.id,"tab-content-registration","the 'tab-content-registration' should be the active tab id");
});

// main()

QUnit.module( "main()" ); 
