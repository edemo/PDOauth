console.log("runnning tests");

QUnit.jUnitReport = function(report) {
	console.log("writing report");
    document.getElementById("qunit-xml").innerHTML = report.xml;
    console.log(report.xml);
};

function ajaxBase(callback) {
	var xmlhttp;
	if (window.XMLHttpRequest)
	  {// code for IE7+, Firefox, Chrome, Opera, Safari
	  xmlhttp=new XMLHttpRequest();
	  }
	else
	  {// code for IE6, IE5
	  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	  }
	var self = this;
	xmlhttp.setRequestHeader = function(name,value) {
		self.header_name = name
		self.header_value = value
	}
	xmlhttp.open = function(method, uri, data) {
		self.method = method
		self.uri = uri
	}
	xmlhttp.send = function(data) {
		self.data = data
		callback(self.status,self.text,self.xml);
	}
	return xmlhttp;	
}

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

assert_IsPopupShown = function( assert ) { assert.ok(document.getElementById("popup").style.display=="flex", "popup div is shown"); }
assert_IsPopupHidden = function( assert ) { assert.ok(document.getElementById("popup").style.display!="flex", "popup div is hidden"); }

QUnit.module( "AJAX" ); 
QUnit.test( "ajaxpost can be mocked", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 201;
	pageScript.text = "szia";
	pageScript.xml = xmlFor("<xml>hello</xml>");
	pageScript.ajaxpost("h",{data: "hello"}, function(status,text,xml) {
		assert.equal(201,status,"callback function gets '201' in the 'status' parameter");
		assert.equal("szia",text,"callback function gets 'Szia' in the 'text' parameter");
		assert.equal("hello",xml.childNodes[0].childNodes[0].nodeValue,"callback function gets an xml data with node value 'hello' in the 'xml' parameter");
	});
	assert.equal(pageScript.uri, "h", "pageScript.uri gets 'h'");
	assert.equal(pageScript.data, "data=hello", "pageScript.data gets 'data=hello'");
	assert.equal(pageScript.method, "POST", "pageScript.method gets 'POST'");
});

QUnit.test( "ajaxget can be mocked", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 201;
	pageScript.text = "szia";
	pageScript.xml = xmlFor("<xml>hello</xml>");
	pageScript.ajaxget("h", function(status,text,xml) {
		assert.equal(201,status,"callback function gets '201' in the 'status' parameter");
		assert.equal("szia",text,"callback function gets 'Szia' in the 'text' parameter");
		assert.equal("hello",xml.childNodes[0].childNodes[0].nodeValue,"callback function gets an xml data with node value 'hello' in the 'xml' parameter");
	});
	assert.equal(pageScript.uri, "h", "pageScript.uri gets 'h'");
	assert.equal(pageScript.method, "GET", "pageScript.method gets 'GET'");
});

// msg=processErrors(data={})

QUnit.module( "processErrors()" ); 
QUnit.test( "message is returned in message property", function( assert ) {
	pageScript = new PageScript(true)
	msg=pageScript.processErrors({message: "hello world"})
	assert.equal(msg.message, "<p>message</p><p>hello world</p>", "the 'message' property of the returned object gets its value");
	assert.equal(msg.title, "Szerverüzenet",  "the 'title' property of the returned object gets its value");
});

QUnit.test( "errors is returned in error property", function( assert ) {
	pageScript = new PageScript(true)
	data={errors: ["hello world"]}
	error="<ul><li>hello world</li></ul>"
	title="Hibaüzenet"
	
	msg=pageScript.processErrors(data)
	assert.equal(msg.error, error, "the 'error' property of the returned object gets its value");
	assert.equal(msg.title, title, "the 'title' property of the returned object gets its value");	
});

QUnit.test( "assurances, email and userid are returned in success property", function( assert ) {
	pageScript = new PageScript(true)
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
QUnit.test( "with displayMsg the popup div apears", function( assert ) {
	pageScript = new PageScript(true)
	assert_IsPopupHidden( assert );
	pageScript.displayMsg({title: "hello world"});
	assert_IsPopupShown( assert );
});

QUnit.test( "with displayMsg string in message property is shown in the PopupWindow_MessageDiv element", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.displayMsg({message: "hello world"})
	assert.equal(document.getElementById("PopupWindow_MessageDiv").innerHTML,"<p class=\"message\">hello world</p>");
});

QUnit.test( "with displayMsg string in error property is shown in the PopupWindow_ErrorDiv element", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.displayMsg({error: "hello world"})
	assert.equal(document.getElementById("PopupWindow_ErrorDiv").innerHTML,"<p class=\"warning\">hello world</p>");	
});

QUnit.test( "with displayMsg string in success property is shown in the PopupWindow_SuccessDiv element", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.displayMsg({success: "hello world"})
	assert.equal(document.getElementById("PopupWindow_SuccessDiv").innerHTML, "<p class=\"success\">hello world</p>");	
});

QUnit.test( "with displayMsg string in title property is shown in the PopupWindow_TitleDiv element", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.displayMsg({title: "hello world"})
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "<h2>hello world</h2>");	
});

// closePopup(callback=function(){})

QUnit.module( "closePopup()" ); 
QUnit.test( "the popup div hides and a callback function is calling", function( assert ) {
	pageScript = new PageScript(true)
	assert_IsPopupShown( assert );
	pageScript.closePopup( function () {
		document.getElementById("PopupWindow_TitleDiv").innerHTML="hello popup"
	})
	assert_IsPopupHidden( assert )
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "hello popup");
});

QUnit.test( "with displayMsg a callback function is injected into the PopupWindow_CloseButton button onclick propoerty", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.displayMsg( 
		{ 
			title: "hello world", 
			callback: function() {
				document.getElementById("PopupWindow_TitleDiv").innerHTML="world hello"
			} 
		} )
	assert_IsPopupShown( assert );
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "<h2>hello world</h2>");
	document.getElementById("PopupWindow_CloseButton").onclick()
	assert.equal(document.getElementById("PopupWindow_TitleDiv").innerHTML, "world hello");
	assert_IsPopupHidden( assert )
});

// parseUserdata( userdata_object )

QUnit.module( "parseUserdata()" ); 
QUnit.test( "parseUserdata parses userdata contained a JSON object to html", function( assert ) {
	pageScript = new PageScript(true)
	userdata=pageScript.parseUserdata({"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"})
	assert.equal(userdata, "<p><b>e-mail cím:</b> my@email.com</p><p><b>felhasználó azonosító:</b> theuserid</p><p><b>hash:</b></p><pre>undefined</pre><p><b>tanusítványok:</b></p><ul><li>test</li><li>foo</li></ul><p><b>hitelesítési módok:</b></p><ul></ul>");	
});

// myCallback( htmlstatus, JSON )

QUnit.module( "myCallback()" ); 
QUnit.test( "MyCallback processes the data through processErrors", function( assert ) {
	pageScript = new PageScript(true)
	data = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	pageScript.myCallback(200,data)
	assert.equal(document.getElementById("PopupWindow_SuccessDiv").innerHTML, "<p class=\"success\"></p>"+pageScript.parseUserdata(JSON.parse(data))+"<p></p>");	
});

// initCallback( htmlstatus, JSON )

QUnit.module( "initCallback()" ); 
QUnit.test( "initCallback hides account and assurer menutabs and shows login and registration if the html status not 200", function( assert ) {
	pageScript = new PageScript(true)
	data = '{"errors": {"": "no authorization"}}'
	pageScript.initCallback(400,data)
	assert.equal(document.getElementById("login-menu").style.display,"block");
	assert.equal(document.getElementById("registration-menu").style.display,"block");
	assert.equal(document.getElementById("assurer-menu").style.display,"none");
	assert.equal(document.getElementById("account-menu").style.display,"none");
	assert_IsPopupHidden( assert )
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
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.passwordReset("PasswordResetForm")
	assert.equal(pageScript.uri, "/v1/password_reset");
	assert.equal(pageScript.data, "secret=thesecret&password=thepassword");
	assert.equal(pageScript.method, "POST");
});

// login()

QUnit.test( "login calls /login with password as credential type, username and password", function( assert ) {
	document.getElementById("LoginForm_username_input").value = "theuser"
	document.getElementById("LoginForm_password_input").value = "thepassword"
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.login()
	assert.equal(pageScript.uri, "/login");
	assert.equal(pageScript.data, "credentialType=password&identifier=theuser&secret=thepassword");
	assert.equal(pageScript.method, "POST");
});

// login_with_facebook

QUnit.test( "login_with_facebook calls /login with facebook as credential type, userid and access token", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.login_with_facebook("fbid", "accesstoken")
	assert.equal(pageScript.uri, "/login");
	assert.equal(pageScript.data, "credentialType=facebook&identifier=fbid&secret=accesstoken");
	assert.equal(pageScript.method, "POST");
});

QUnit.test( "byEmail calls /v1/user_by_email/[email address]", function( assert ) {
	document.getElementById("ByEmailForm_email_input").value = "email@address.com"
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.byEmail()
	assert.equal(pageScript.uri, "/v1/user_by_email/email%40address.com");
	assert.equal(pageScript.method, "GET");
});

QUnit.test( "register calls /v1/register with all the data needed for registration", function( assert ) {
	document.getElementById("RegistrationForm_credentialType_input").value = "password";
	document.getElementById("RegistrationForm_identifier_input").value = "identifier";
	document.getElementById("RegistrationForm_secret_input").value = "secret";
	document.getElementById("RegistrationForm_email_input").value = "email@mail.com";
	document.getElementById("RegistrationForm_digest_input").value = "thedigest";
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.register()
	assert.equal(pageScript.uri, "/v1/register");
	assert.equal(pageScript.data, "credentialType=password&identifier=identifier&secret=secret&email=email%40mail.com&digest=thedigest");
	assert.equal(pageScript.method, "POST");
});

QUnit.test( "register_with_facebook calls /v1/register with all the data needed for facebook registration", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.register_with_facebook("userId", "accessToken", "email@example.com");
	assert.equal(pageScript.uri, "/v1/register");
	assert.equal(pageScript.data, "credentialType=facebook&identifier=userId&secret=accessToken&email=email%40example.com");
	assert.equal(pageScript.method, "POST");
});

QUnit.test( "getCookie extracts the named cookie", function( assert ) {
	pageScript = new PageScript(true)
	document.cookie = "csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"
	cookie = pageScript.getCookie('csrf')
	assert.equal(cookie, "64b0d60d-0d6f-4c47-80d5-1a698f67d2ef");
});

QUnit.test( "addAssurance calls /v1/add_assurance with digest,assurance and email", function( assert ) {
	document.getElementById("AddAssuranceForm_digest_input").value="digest"
	document.getElementById("AddAssuranceForm_assurance_input").value="assurance"
	document.getElementById("AddAssuranceForm_email_input").value="email@e.mail";
	document.cookie = "csrf=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef"

	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.addAssurance();
	assert.equal(pageScript.uri, "/v1/add_assurance");
	assert.equal(pageScript.data, "digest=digest&assurance=assurance&email=email%40e.mail&csrf_token=64b0d60d-0d6f-4c47-80d5-1a698f67d2ef");
	assert.equal(pageScript.method, "POST");
});

QUnit.test( "digestGetter puts the result for the predigest input to the digest for the named form", function( assert ) {
	document.getElementById("AddAssuranceForm_predigest_input").value="xxpredigestxx"

	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '<hash>thehash</hash>';
	pageScript.xml = xmlFor(pageScript.text);
	pageScript.digestGetter("AddAssuranceForm").getDigest();
	assert.equal(document.getElementById("AddAssuranceForm_digest_input").value,"thehash")
	assert.equal(pageScript.uri, "https://anchor.edemokraciagep.org/anchor");
	assert.equal(pageScript.data, "<id>xxpredigestxx</id>");
	assert.equal(pageScript.method, "POST");
});

// menuHandler("menuName")

QUnit.test( "menuHandler can hide and display the tabs", function( assert ) {
	document.getElementById("login-menu").style.display="block";
	pageScript = new PageScript(true)
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
