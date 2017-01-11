// mocked and common functions
		console.log("mocking")
		var xmlFor=function(text) {
			if (window.DOMParser) {
				parser=new DOMParser();
				xmlDoc=parser.parseFromString(text,"text/xml");
			} else {
				xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
				xmlDoc.async=false;
				xmlDoc.loadXML(text);
			}  
			return xmlDoc;
		},
		
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
		},

		testXMLHttpRequestObject = function( arg ) {
			var me = this;
			this.oName = "XMLHttpRequest"
			this.arg=arg || "undefined";
			commonAjaxTestMethods(me)
		},

		testActiveXHttpRequestObject = function(arg) {
			var me = this;
			this.arg=arg || "undefined";
			this.oName="ActiveXObject"
			commonAjaxTestMethods(me)
		},

		hideMessageBox = function () {  // hides and clears the message-container
			document.getElementById("message-container").innerHTML   = "";
			document.getElementById('message-container').style.display = 'none';
		},

		isMessageBoxShown = function() { return document.getElementById("message-container").style.display=="block"; },
		isMessageBoxHidden = function() { return document.getElementById("message-container").style.display!="block"; },

		isLoginButtonHidden        = function() { return document.getElementById("login-menu").style.display=="none" },
		isRegistrationButtonHidden = function() { return document.getElementById("registration-menu").style.display=="none" },
		isAssurerButtonHidden      = function() { return document.getElementById("assurer-menu").style.display=="none" },
		isAccountButtonHidden      = function() { return document.getElementById("account-menu").style.display=="none" },
		isApplicationButtonHidden  = function() { return document.getElementById("application-menu").style.display=="none" },
		isCredentialContainerEmpty = function() { return document.getElementById("Remove_Credential_Container").innerHTML==""},
		
		doesContainerContain = function(container,testStrings) {
			for(testString in testStrings){
				if (!document.getElementById(container).innerHTML.search(testString)) return false;
			}
			return true;
		},

		doesCredentialContainerContain = function(testStrings) {
			return doesContainerContain("Remove_Credential_Container", testStrings);
		},

		doesMessageContainerContain = function(testStrings) {
			return doesContainerContain("MessageBoxWindow_MessageDiv", testStrings);
		},

		doesSuccessContainerContain = function(testStrings) {
			return doesContainerContain("MessageBoxWindow_SuccessDiv", testStrings);
		},

		doesErrorContainerContain = function(testStrings) {
			return doesContainerContain("MessageBoxWindow_ErrorDiv", testStrings);
		},

		doesTitleContainerContain = function(testStrings) {
			return doesContainerContain("MessageBoxWindow_ErrorDiv", testStrings);
		},

		doesMeContainerContain = function(testStrings) {
			return doesContainerContain("me_Msg", testStrings);
		},

		assert_IsMessageBoxShown = function( assert ) { assert.ok(isMessageBoxShown(), "MessageBox div should be shown"); },
		assert_IsMessageBoxHidden = function( assert ) { assert.ok(isMessageBoxHidden(), "MessageBox div should be hidden"); },

		callbackForAJAXtest = function(status,text,xml) {
			pageScript.callbackArgs = {
				status: status,
				text: text,
				xml: xml
				}
		},

		makeResponseDataForAJAXtest = function () {
			pageScript.status = 201;
			pageScript.text   = "szia";
			pageScript.xml    = xmlFor("<xml>hello</xml>");
		},

		test = {
			win: {
				XMLHttpRequest: testXMLHttpRequestObject,
				location: window.location
				},
			debug: true,
			uribase: "/ada"
		}
		
QUnit.jUnitReport = function(report) {
	console.log("writing report");
    QUnit.XmlContainer.innerHTML = report.xml;
//    console.log(report.xml);
};		
		
