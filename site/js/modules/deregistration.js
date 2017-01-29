 import PageScript from './script'
 import { _ } from './gettext'
 import { gettext } from './gettext'
 
 (function(){	
	var self
	PageScript.prototype.page = "deregistration";
	PageScript.prototype.main = function() {
		self=this.getThis()
		var xxxx=self
		this.ajaxget("/adauris", self.callback(self.commonInit), true)
		window.traces.push("main end")
	}
	
	PageScript.prototype.initialise = function(text) {
		self.ajaxget("locale/hu.json",self.callback(self.gettextCallback, function(response){
			gettext.mockGettext()
			self.displayServerResponse(response, {ok: self.init_})
		} ),true)
		window.traces.push("initialise")
	}
	
	PageScript.prototype.gettextCallback = function(response){
		gettext.initGettext(response)
		self.init_()
	} 
	
	PageScript.prototype.init_=function(){
		self.ajaxget("/v1/users/me", self.callback(self.userIsLoggedIn, self.userNotLoggedIn))	
		window.traces.push("init_")		
	}

	PageScript.prototype.userIsLoggedIn = function( response ) {
		self.isLoggedIn=true
		self.refreshTheNavbar()
		window.traces.push('userIsLoggedIn')
	}
	
	PageScript.prototype.userNotLoggedIn = function( response ) {
		var data = self.validateServerMessage( response );
		if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
		self.refreshTheNavbar()
	}
	
	PageScript.prototype.displayMsg = function( msg ) {
		if (!(msg.title || msg.error || msg.message || msg.success)) return
		$("#myModal").modal();
		if (!msg.callback) msg.callback="";
		this.msgCallback=msg.callback; //only for testing
		document.getElementById("PopupWindow_CloseButton1").onclick = function() {self.closePopup(msg.callback)}
		document.getElementById("PopupWindow_CloseButton2").onclick = function() {self.closePopup(msg.callback)}
		document.getElementById("PopupWindow_TitleDiv").innerHTML = msg.title;
		document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
		document.getElementById("PopupWindow_MessageDiv").innerHTML = "";
		document.getElementById("PopupWindow_SuccessDiv").innerHTML = ""		
		if (msg.title) document.getElementById("PopupWindow_TitleDiv").innerHTML = msg.title;
		if (msg.error) document.getElementById("PopupWindow_ErrorDiv").innerHTML     = "<p class='warning'>"+msg.error+"</p>";
		if (msg.message) document.getElementById("PopupWindow_MessageDiv").innerHTML = "<p class='message'>"+msg.message+"</p>";
		if (msg.success)document.getElementById("PopupWindow_SuccessDiv").innerHTML  = "<p class='success'>"+msg.success+"</p>";
		window.traces.push("MSGbox ready")
	}

	PageScript.prototype.closePopup = function(popupCallback) {
		this.popupCallback=popupCallback //only for testing
		document.getElementById("PopupWindow_TitleDiv").innerHTML   = "";
		document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
		document.getElementById("PopupWindow_MessageDiv").innerHTML    = "";
		document.getElementById("PopupWindow_SuccessDiv").innerHTML = "";
		if (popupCallback) popupCallback();
		window.traces.push("popup closed")
		return "closePopup";
	}

	PageScript.prototype.doDeregister = function() {
		
		var deregisterCallback = function( response ) {
			self.isLoggedIn = false
			self.refreshTheNavbar();
			if ( self.page == "account" ) self.displayTheSection( "login" );
			self.displayServerResponse( response, {ok: self.doLoadHome} )
		}
		
		if ( document.getElementById("accept_deregister").checked ) {
			if ( self.QueryString.secret ) {
				var post = {
					csrf_token: self.getCookie("csrf"),
					deregister_secret: self.QueryString.secret
				}
				self.ajaxpost( "/v1/deregister_doit", post, self.callback( deregisterCallback ) )
			}
			else self.displayMsg({
					title:_("Error message"),
					error:_("The secret is missing")
			})
		}
		else self.displayMsg({
			title:_("Error message"),
			error:_("To accept the terms please mark the checkbox!")
		})			
	}
	
}()
)

export var pageScript = new PageScript()