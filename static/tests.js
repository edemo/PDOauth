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

QUnit.test( "ajaxpost can be mocked", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 201;
	pageScript.text = "szia";
	pageScript.xml = xmlFor("<xml>hello</xml>");
	pageScript.ajaxpost("h",{data: "hello"}, function(status,text,xml) {
		assert.equal(201,status);
		assert.equal("szia",text);
		assert.equal("hello",xml.childNodes[0].childNodes[0].nodeValue);
	});
	assert.equal(pageScript.uri, "h");
	assert.equal(pageScript.data, "data=hello");
	assert.equal(pageScript.method, "POST");
});

QUnit.test( "ajaxget can be mocked", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 201;
	pageScript.text = "szia";
	pageScript.xml = xmlFor("<xml>hello</xml>");
	pageScript.ajaxget("h", function(status,text,xml) {
		assert.equal(201,status);
		assert.equal("szia",text);
		assert.equal("hello",xml.childNodes[0].childNodes[0].nodeValue);
	});
	assert.equal(pageScript.uri, "h");
	assert.equal(pageScript.data, undefined);
	assert.equal(pageScript.method, "GET");
});

QUnit.test( "with processErrors message is shown in the message element", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.processErrors({message: "hello world"})
	assert.equal(document.getElementById("message").innerHTML,"hello world");
	document.getElementById("message").innerHTML = "";
});

QUnit.test( "with processErrors errors are shown in the errorMsg element", function( assert ) {
	pageScript = new PageScript(true)
	pageScript.processErrors({errors: ["hello world"]})
	assert.equal(document.getElementById("errorMsg").innerHTML,"<ul><li>hello world</li></ul>");	
});

QUnit.test( "with processErrors assurances, email and userid are shown in the userdata element", function( assert ) {
	pageScript = new PageScript(true)
	data = {
                'assurances': {
                        'test': '',
                        'foo': ''
                },
                'email': 'my@email.com',
                'userid': 'theuserid'
        }
	
	pageScript.processErrors(data)
	assert.equal(document.getElementById("userdata").innerHTML,
		"email: my@email.com<br>userid: theuserid<br>hash: undefined<br>assurances:<ul><li>test</li><li>foo</li></ul><br>credentials:<ul></ul>");	
});

QUnit.test( "MyCallback processes the data through processErrors", function( assert ) {
	pageScript = new PageScript(true)
	data = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}'
	pageScript.myCallback(200,data)
	assert.equal(document.getElementById("userdata").innerHTML,
		"email: my@email.com<br>userid: theuserid<br>hash: undefined<br>assurances:<ul><li>test</li><li>foo</li></ul><br>credentials:<ul></ul>");	
});

QUnit.test( "passwordReset calls /v1/password_reset with secret and password", function( assert ) {
	document.getElementById("PasswordResetForm_secret_input").value = "thesecret"
	document.getElementById("PasswordResetForm_password_input").value = "thepassword"
	pageScript = new PageScript(true)
	pageScript.ajaxBase = ajaxBase
	pageScript.status = 200;
	pageScript.text = '{"userid": "theuserid", "assurances": {"test": "", "foo": ""}, "email": "my@email.com"}';
	pageScript.passwordReset()
	assert.equal(pageScript.uri, "/v1/password_reset");
	assert.equal(pageScript.data, "secret=thesecret&password=thepassword");
	assert.equal(pageScript.method, "POST");
});

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
