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
		pageScript.data = data
		pageScript.callback=me.callback
		me.callback(pageScript.status,pageScript.text,pageScript.xml);
	}
	me.open = function(method, uri, data) {
		pageScript.method = method
		pageScript.uri = uri
	}
	me.setRequestHeader = function(name,value) {
		pageScript.header_name = name
		pageScript.header_value = value
	}
}

testXMLHttpRequestObject = function(arg) {
	var me = this;
	this.oName="XMLHttpRequest"
	this.arg=arg || "undefined";
	commonAjaxTestMethods(me)
}

testActiveXHttpRequestObject = function(arg) {
	var me = this;
	this.arg=arg || "undefined";
	this.oName="ActiveXObject"
	commonAjaxTestMethods(me)
}

hidePopup = function () {
		document.getElementById("PopupWindow_TitleDiv").innerHTML   = "";
		document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
		document.getElementById("PopupWindow_MessageDiv").innerHTML    = "";
		document.getElementById("PopupWindow_SuccessDiv").innerHTML = "";
		document.getElementById('popup').style.display='none';
		document.getElementById('fade').style.display='none';
}

IsPopupShown = function() { return document.getElementById("popup").style.display=="flex"; }
IsPopupHidden = function() { return document.getElementById("popup").style.display!="flex"; }

assert_IsPopupShown = function( assert ) { assert.ok(IsPopupShown(), "popup div should be shown"); }
assert_IsPopupHidden = function( assert ) { assert.ok(IsPopupHidden(), "popup div should be hidden"); }

callbackForAjax = function(status,text,xml) {
	assert = pageScript.assert
	assert.equal(201,status,"callback function gets '201' in the 'status' parameter");
	assert.equal("szia",text,"callback function gets 'Szia' in the 'text' parameter");
	assert.equal("hello",xml.childNodes[0].childNodes[0].nodeValue,"callback function gets an xml data with node value 'hello' in the 'xml' parameter");
}

dataForAJAX = function () {
	pageScript.status = 201;
	pageScript.text = "szia";
	pageScript.xml = xmlFor("<xml>hello</xml>");
}

var test={ win: { XMLHttpRequest: testXMLHttpRequestObject }, debug: true }

console.log("runnning tests");

QUnit.jUnitReport = function(report) {
	console.log("writing report");
    document.getElementById("qunit-xml").innerHTML = report.xml;
    console.log(report.xml);
};

QUnit.module( "qeryStringFunc" ); 
QUnit.test( "should return an array of query strings of url", function( assert ) {
	var loc = { location: { search: "?something=y&otherthing=q&something=x&something=z" } } 
	var qs = QueryStringFunc( loc );
	data={}
	data["something"]=["y","x","z"];
	data["otherthing"]="q";
	
	assert.equal(JSON.stringify(qs),JSON.stringify(data), "the arrays should equal" );
})

QUnit.module( "AJAX" ); 
QUnit.test( "ajaxbase should return with a xmlhttp object ", function( assert ) {
	
	pageScript = new PageScript(test)
	delete test.win.XMLHttpRequest
	test.win.ActiveXObject= testActiveXHttpRequestObject  // IE style httpRequest
	pageScript.assert = assert
	assert.expect( 7 );

	var xmlhttp = pageScript.ajaxBase(callbackForAjax);
	assert.equal(xmlhttp.oName, "ActiveXObject", "if XMLHttpRequest isn't defined, should return with an 'ActiveXObject' ");
	assert.equal(xmlhttp.arg, "Microsoft.XMLHTTP", "ActiveXObject calling argument should be 'Microsoft.XMLHTTP'");
	
	//the parameters should be got
	xmlhttp.status = 201
	xmlhttp.responseText = "szia";
	xmlhttp.responseXML = xmlFor("<xml>hello</xml>");
	xmlhttp.readyState=1
	xmlhttp.onreadystatechange(); //nothing should be happend  
	xmlhttp.readyState=4
	xmlhttp.onreadystatechange(); //callback should be called, argument check is defined in the callback

	test.win.XMLHttpRequest= testXMLHttpRequestObject; // non IE style httpRequest
	xmlhttp = pageScript.ajaxBase(callbackForAjax);
	assert.equal(xmlhttp.oName, "XMLHttpRequest", "if XMLHttpRequest defined, should return with an 'XMLHttpRequest' ");
	assert.equal(xmlhttp.arg, "undefined", "XMLHttpRequest call shouldn't have any argument");
});

QUnit.test( "ajaxpost can be mocked", function( assert ) {
	
	pageScript = new PageScript(test)
	dataForAJAX();
	pageScript.assert = assert
	
	pageScript.ajaxpost("h",{data: "hello"}, callbackForAjax );
	assert.equal(pageScript.uri, "h", "pageScript.uri gets 'h'");
	assert.equal(pageScript.data, "data=hello", "pageScript.data gets 'data=hello'");
	assert.equal(pageScript.method, "POST", "pageScript.method gets 'POST'");
});

QUnit.test( "ajaxget can be mocked", function( assert ) {
	
	pageScript = new PageScript(test)
	test.win.XMLHttpRequest= testXMLHttpRequestObject;
	dataForAJAX();
	pageScript.assert = assert
	
	pageScript.ajaxget("h", callbackForAjax);
	assert.equal(pageScript.uri, "h", "pageScript.uri gets 'h'");
	assert.equal(pageScript.method, "GET", "pageScript.method gets 'GET'");
});

// msg=processErrors(data={})

QUnit.module( "processErrors()" ); 
QUnit.test( "message is returned in message property", function( assert ) {
	
	pageScript = new PageScript(test)
	
	msg = pageScript.processErrors({message: "hello world"})
	assert.equal(msg.message, "<p>message</p><p>hello world</p>", "the 'message' property of the returned object gets its value");
	assert.equal(msg.title, "Szerverüzenet",  "the 'title' property of the returned object gets its value");
});

QUnit.test( "errors is returned in error property", function( assert ) {
	
	pageScript = new PageScript(test)
	data  = {errors: ["hello world"]}
	error = "<ul><li>hello world</li></ul>"
	title = "Hibaüzenet"
	
	msg = pageScript.processErrors(data)
	assert.equal(msg.error, error, "the 'error' property of the returned object gets its value");
	assert.equal(msg.title, title, "the 'title' property of the returned object gets its value");	
});

QUnit.test( "assurances, email and userid are returned in success property", function( assert ) {
	
	pageScript = new PageScript(test)
	data = {
                'assurances': {
                        'test': '',
                        'foo': ''
                },
                'email': 'my@email.com',
                'userid': 'theuserid'
        }
	success="<p><b>e-mail cím:</b> my@email.com</p><p><b>felhasználó azonosító:</b> theuserid</p><p><b>hash:</b></p><pre>undefined</pre><p><b>tanusítványok:</b></p><ul><li>test</li><li>foo</li></ul><p><b>hitelesítési módok:</b></p><ul></ul>"
	title="A felhasználó adatai"
	
	msg=pageScript.processErrors(data)
	assert.equal(msg.success, success, "the 'success' property of the returned object gets its value");	
	assert.equal(msg.title, title, "the 'title' property of the returned object gets its value");	
});

// displayMsg(msg={})

QUnit.module( "displayMsg()" ); 
QUnit.test( "the 'popup' div should be appeared", function( assert ) {
	pageScript = new PageScript(test)
	document.getElementById("popup").style.display="none";
	pageScript.displayMsg({title: "hello world"});
	assert_IsPopupShown( assert );
});

QUnit.test( "the strings comes with 'error', 'succes', 'title' and 'messege' property of the input object should be shown in their dedicated div element", function( assert ) {
	pageScript = new PageScript(test)
	msg={ 
		message: "hello world",
		error: "hello world",
		success: "hello world",
		title: "hello world"
		}
	message_div_content="<p class=\"message\">hello world</p>"
	error_div_content="<p class=\"warning\">hello world</p>"
	success_div_content="<p class=\"success\">hello world</p>"
	title_div_content="<h2>hello world</h2>"
	
	pageScript.displayMsg(msg)
	assert.equal(document.getElementById("PopupWindow_MessageDiv").innerHTML, message_div_content, "string in message property should be shown in the PopupWindow_MessageDiv element");
	assert.equal(document.getElementById("PopupWindow_ErrorDiv").innerHTML,error_div_content, "string in error property should be shown in the PopupWindow_ErrorDiv element");	
	assert.equal(document.getElementById("PopupWindow_SuccessDiv").innerHTML,success_div_content, "string in success property should be shown in the PopupWindow_SuccessDiv element");	
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, title_div_content, "string in title property should be shown in the PopupWindow_TitleDiv element");		
	});


QUnit.test( "the callback function should be injected into the PopupWindow_CloseButton button onclick propoerty", function( assert ) {
	pageScript = new PageScript(test)
	msg={ 
			title: "hello world", 
			callback: function() { return 'world hello' } 
		}
	
	pageScript.displayMsg( msg )
	assert_IsPopupShown( assert );
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "<h2>hello world</h2>", "the popup window's title div should get its value");
	document.getElementById("PopupWindow_CloseButton").onclick()
	assert_IsPopupHidden( assert );
	assert.equal( pageScript.popupCallback.toString(), msg.callback.toString() , "the function in onclick property should get the function in msg.callback as argument'")

	delete msg.callback
	pageScript.displayMsg( msg )
	assert_IsPopupShown( assert );
	document.getElementById("PopupWindow_CloseButton").onclick()
	assert_IsPopupHidden( assert );
	assert.equal( pageScript.popupCallback.toString(), "", "the onclick function shouldn't get any argumentum")
});

// closePopup(callback=function(){})

QUnit.module( "closePopup()" ); 
QUnit.test( "the popup div should hide, erase its child divs and the callback function should be callable", function( assert ) {
	pageScript = new PageScript(test)
	pageScript.assert = assert
	callback = function () { pageScript.assert.ok( true, "should true if callback is called" )}
	document.getElementById("PopupWindow_TitleDiv").innerHTML='valami'
	document.getElementById("PopupWindow_SuccessDiv").innerHTML='valami'
	document.getElementById("PopupWindow_ErrorDiv").innerHTML='valami'
	document.getElementById("PopupWindow_MessageDiv").innerHTML='valami'
	
	assert.expect( 6 )
	pageScript.closePopup( callback )
	assert_IsPopupHidden( assert )
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "", "the 'PopupWindow_TitleDiv' should be empty");
	assert.equal(document.getElementById("PopupWindow_SuccessDiv").innerHTML, "", "the 'PopupWindow_SuccessDiv' should be empty");
	assert.equal(document.getElementById("PopupWindow_MessageDiv").innerHTML, "", "the 'PopupWindow_MessageDiv' should be empty");
	assert.equal(document.getElementById("PopupWindow_ErrorDiv").innerHTML, "", "the 'PopupWindow_ErrorDiv' should be empty");
});

// parseUserdata( userdata_object )

QUnit.module( "parseUserdata()" ); 
QUnit.test( "should parse the userdata contained an object to html", function( assert ) {
	pageScript = new PageScript(test)
	var theUserId    = "theuserid"
	var theUserEmail = "my@email.com"
	var theDataObject = {
							"userid": theUserId,
						"assurances": {"test": "", "foo": ""},
							 "email": theUserEmail 
						}
	
	var userData = pageScript.parseUserdata(theDataObject)
	assert.ok( userData.search(theUserId), "the output should contain the userid" )
	assert.ok( userData.search(theUserEmail), "the output should contain the email address" )
});

// myCallback( htmlstatus, JSON_string )

QUnit.module( "myCallback()" ); 
QUnit.test( "should redirect with 'next' query var comes in url if status=200", function( assert ) {
	pageScript = new PageScript(test)
	data = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	QueryString.next = "newlocation"
	
	pageScript.myCallback( 201, data )
	assert.notOk(win.location, "with status 201 the window.location shouldn't get new value accordin to QueryString.next");	
	pageScript.myCallback( 200, data )
	assert.equal(win.location, "newlocation", "with status 200 the window.location should get the new location");	

	delete QueryString.next
	delete win.location
	
	pageScript.myCallback( 200, data )
	assert.notOk(win.location, "with status 200 the window.location shouldn't get new value if QueryString.next undefined");
	hidePopup()
});

QUnit.test( "should display the processed data through processErrors() and displayMsg(), popop callback should have the get_me()", function( assert ) {
	pageScript = new PageScript(test)
	data = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	pageScript.myCallback( 200,data )
	assert_IsPopupShown( assert );
	assert.ok(document.getElementById("PopupWindow_SuccessDiv").innerHTML.search("my@email.com"), "the data should be shown in popup window");	
	assert.equal( pageScript.msg.callback, pageScript.get_me.toString() , "the function in PopupWindow_CloseButton onclick property should get the function 'get_me' as argument'")
	hidePopup();
});

// get_me() calls /v1/users/me

QUnit.module( "get_me()" ); 
QUnit.test( "should call '/v1/users/me' trough AJAX", function( assert ) {
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.get_me();
	assert.equal(pageScript.uri, "/v1/users/me", "the URI should be '/v1/users/me'");
	assert.equal(pageScript.method, "GET", "the method should be GET");
	assert.equal(pageScript.callback.toString(), pageScript.initCallback.toString(), "callback function should be the 'initCallback'");
});

// initCallback( htmlstatus, JSON )
// ez még nincs kész
QUnit.module( "initCallback()" ); 
QUnit.test( "initCallback hides account and assurer menutabs and shows login and registration if the html status not 200", function( assert ) {
	pageScript = new PageScript(test)
	data = '{"errors": {"": "no authorization"}}'
	pageScript.initCallback(400,data)
	assert.equal(document.getElementById("login-menu").style.display,"block");
	assert.equal(document.getElementById("registration-menu").style.display,"block");
	assert.equal(document.getElementById("assurer-menu").style.display,"none");
	assert.equal(document.getElementById("account-menu").style.display,"none");
	assert_IsPopupShown( assert )
	data = '{"errors": {"": "any other error message"}}'
	pageScript.initCallback(400,data)
	assert.equal(document.getElementById("login-menu").style.display,"block");
	assert.equal(document.getElementById("registration-menu").style.display,"block");
	assert.equal(document.getElementById("assurer-menu").style.display,"none");
	assert.equal(document.getElementById("account-menu").style.display,"none");
	assert_IsPopupShown( assert );
});


// passwordReset("formName")

QUnit.module( "passwordReset()" ); 
QUnit.test( "passwordReset calls /v1/password_reset with secret and password", function( assert ) {
	document.getElementById("PasswordResetForm_secret_input").value = "thesecret"
	document.getElementById("PasswordResetForm_password_input").value = "thepassword"
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.passwordReset("PasswordResetForm")
	assert.equal(pageScript.uri, "/v1/password_reset");
	assert.equal(pageScript.data, "secret=thesecret&password=thepassword");
	assert.equal(pageScript.method, "POST");
});

// InitiatePasswordReset(formName)
QUnit.module( "InitiatePasswordReset()" ); 

// login()

QUnit.module( "login()" ); 
QUnit.test( "login calls /login with password as credential type, username and password", function( assert ) {
	document.getElementById("LoginForm_username_input").value = "theuser"
	document.getElementById("LoginForm_password_input").value = "thepassword"
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.login()
	assert.equal(pageScript.uri, "/login");
	assert.equal(pageScript.data, "credentialType=password&identifier=theuser&secret=thepassword");
	assert.equal(pageScript.method, "POST");
});

// login_with_facebook

QUnit.module( "login_with_facebook()" ); 
QUnit.test( "login_with_facebook calls /login with facebook as credential type, userid and access token", function( assert ) {
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.login_with_facebook("fbid", "accesstoken")
	assert.equal(pageScript.uri, "/login");
	assert.equal(pageScript.data, "credentialType=facebook&identifier=fbid&secret=accesstoken");
	assert.equal(pageScript.method, "POST");
});

// byEmail

QUnit.module( "byEmail()" ); 
QUnit.test( "byEmail calls /v1/user_by_email/[email address]", function( assert ) {
	document.getElementById("ByEmailForm_email_input").value = "email@address.com"
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.byEmail()
	assert.equal(pageScript.uri, "/v1/user_by_email/email%40address.com");
	assert.equal(pageScript.method, "GET");
});

// logoutCallback()

QUnit.module( "logoutCallback()" ); 

// logout()

QUnit.module( "logout()" ); 

// uriCallback()

QUnit.module( "uriCallback()" ); 

// sslLogin()

QUnit.module( "sslLogin()" ); 

// register

QUnit.module( "register()" ); 
QUnit.test( "register calls /v1/register with all the data needed for registration", function( assert ) {
	document.getElementById("RegistrationForm_credentialType_input").value = "password";
	document.getElementById("RegistrationForm_identifier_input").value = "identifier";
	document.getElementById("RegistrationForm_secret_input").value = "secret";
	document.getElementById("RegistrationForm_email_input").value = "email@mail.com";
	document.getElementById("RegistrationForm_digest_input").value = "thedigest";
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.register()
	assert.equal(pageScript.uri, "/v1/register");
	assert.equal(pageScript.data, "credentialType=password&identifier=identifier&secret=secret&email=email%40mail.com&digest=thedigest");
	assert.equal(pageScript.method, "POST");
});

// add_facebook_credential()

QUnit.module( "add_facebook_credential()" ); 

// register_with_facebook

QUnit.module( "register_with_facebook()" ); 
QUnit.test( "register_with_facebook calls /v1/register with all the data needed for facebook registration", function( assert ) {
	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.register_with_facebook("userId", "accessToken", "email@example.com");
	assert.equal(pageScript.uri, "/v1/register");
	assert.equal(pageScript.data, "credentialType=facebook&identifier=userId&secret=accessToken&email=email%40example.com");
	assert.equal(pageScript.method, "POST");
});

// getCookie

QUnit.module( "getCookie()" ); 
QUnit.test( "getCookie extracts the named cookie", function( assert ) {
	test.win.document = {cookie:"csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"}
	pageScript = new PageScript(test)
	cookie = pageScript.getCookie('csrf')
	assert.equal(cookie, "64b0d60d-0d6f-4c47-80d5-1a698f67d2ef");
});

// addAssurance

QUnit.module( "addAssurance()" ); 
QUnit.test( "addAssurance calls /v1/add_assurance with digest,assurance and email", function( assert ) {
	document.getElementById("AddAssuranceForm_digest_input").value="digest"
	document.getElementById("AddAssuranceForm_assurance_input").value="assurance"
	document.getElementById("AddAssuranceForm_email_input").value="email@e.mail";
	document.cookie = "csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"

	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.addAssurance();
	assert.equal(pageScript.uri, "/v1/add_assurance");
	assert.equal(pageScript.data, "digest=digest&assurance=assurance&email=email%40e.mail&csrf_token=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef");
	assert.equal(pageScript.method, "POST");
});

// hashCallback

QUnit.module( "hashCallback()" ); 

// InitiateResendRegistrationEmail

QUnit.module( "InitiateResendRegistrationEmail()" ); 

// changeHash

QUnit.module( "changeHash()" ); 

// digestGetter

QUnit.module( "digestGetter()" ); 
QUnit.test( "digestGetter puts the result for the predigest input to the digest for the named form", function( assert ) {
	document.getElementById("AddAssuranceForm_predigest_input").value="xxpredigestxx"

	pageScript = new PageScript(test)
	pageScript.status = 200;
	pageScript.text = '<hash>thehash</hash>';
	pageScript.xml = xmlFor(pageScript.text);
	pageScript.digestGetter("AddAssuranceForm").getDigest();
	assert.equal(document.getElementById("AddAssuranceForm_digest_input").value,"thehash")
	assert.equal(pageScript.uri, "https://anchor.edemokraciagep.org/anchor");
	assert.equal(pageScript.data, "<id>xxpredigestxx</id>");
	assert.equal(pageScript.method, "POST");
});

// changeEmailAddress

QUnit.module( "changeEmailAddress()" ); 

// fill_RemoveCredentialContainer

QUnit.module( "fill_RemoveCredentialContainer()" ); 

// RemoveCredential

QUnit.module( "RemoveCredential()" ); 

// addGoogleCredential()

QUnit.module( "addGoogleCredential()" ); 

// GoogleLogin()

QUnit.module( "GoogleLogin()" ); 

// GoogleRegister()

QUnit.module( "GoogleRegister()" ); 

// TwitterLogin()

QUnit.module( "TwitterLogin()" ); 

// addPassowrdCredential()

QUnit.module( "addPassowrdCredential()" ); 

// addCredential()

QUnit.module( "addCredential()" ); 

// deRegister()

QUnit.module( "deRegister()" ); 

// menuHandler("menuName")

QUnit.module( "menuHandler()" ); 
QUnit.test( "menuHandler can hide and display the tabs", function( assert ) {
	document.getElementById("login-menu").style.display="block";
	pageScript = new PageScript(test)
	pageScript.menuHandler("login").menuHide();
	assert.equal(document.getElementById("login-menu").style.display,"none");
	pageScript.menuHandler("login").menuUnhide();
	assert.equal(document.getElementById("login-menu").style.display,"block");
	document.getElementById("login-menu").className="";
	document.getElementById("tab-content-login").style.display="none";
	pageScript.menuHandler("login").menuActivate();
	assert.equal(document.getElementById("login-menu").className,"active-menu");
	assert.equal(document.getElementById("tab-content-login").style.display,"block");
	assert.equal(pageScript.activeButtonName,"login");
	assert.equal(pageScript.activeButton.id,"login-menu");
	assert.equal(pageScript.activeTab.id,"tab-content-login");
	pageScript.menuHandler("registration").menuActivate();
	assert.equal(document.getElementById("login-menu").className,"");
	assert.equal(document.getElementById("tab-content-login").style.display,"none");
	pageScript.menuHandler("registration");
	assert.equal(pageScript.activeButtonName,"registration");
	assert.equal(pageScript.activeButton.id,"registration-menu");
	assert.equal(pageScript.activeTab.id,"tab-content-registration");
});

// main()

QUnit.module( "main()" ); 
