(function(){	
	var self
	PageScript.prototype.page = "account";
	PageScript.prototype.main = function() {
		self=this.getThis()
		xxxx=self
		this.ajaxget("/adauris", self.uriCallback)
		var section = self.QueryString.section
		console.log("section:"+section)
			switch (section) {
				case "all" :
				[].forEach.call( document.getElementsByClassName("func"), function (e) { e.style.display="block"; } );
					break;
				case "registration" :
					self.QueryString.section="register"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "account" :
					self.QueryString.section="my_account"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "pwreset" :
					self.QueryString.section="password_reset"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "deregistration" :
					self.QueryString.section="deregistration"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "emailcheck" :
					self.modNavbarItem();
					self.QueryString.section="email_verification"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "login" :
					self.unhideSection(section+"_section")
					break;
				default:
			}
		
		if (self.QueryString.secret) {
			document.getElementById("PasswordResetForm_secret_input").value=self.QueryString.secret
		}
	}
	PageScript.prototype.modNavbarItem=function(){
		document.getElementById("")
	}
	PageScript.prototype.hideAllSection=function(){
		[].forEach.call( document.getElementsByClassName("func"), function (e) { e.style.display="none"; } );
	}
	
	PageScript.prototype.unhideSection=function(section) {
		document.getElementById(section).style.display="block";
	}

	PageScript.prototype.displayMsg = function( msg ) {
		if (!(msg.title || msg.error || msg.message || msg.success)) return
		$("#myModal").modal();
		if (!msg.callback) msg.callback="";
		this.msgCallback=msg.callback; //only for testing
		document.getElementById("PopupWindow_CloseButton").onclick = function() {self.closePopup(msg.callback)}
		document.getElementById("PopupWindow_TitleDiv").innerHTML = msg.title;
		document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
		document.getElementById("PopupWindow_MessageDiv").innerHTML = "";
		document.getElementById("PopupWindow_SuccessDiv").innerHTML = ""		
		if (msg.title) document.getElementById("PopupWindow_TitleDiv").innerHTML = msg.title;
		if (msg.error) document.getElementById("PopupWindow_ErrorDiv").innerHTML     = "<p class='warning'>"+msg.error+"</p>";
		if (msg.message) document.getElementById("PopupWindow_MessageDiv").innerHTML = "<p class='message'>"+msg.message+"</p>";
		if (msg.success)document.getElementById("PopupWindow_SuccessDiv").innerHTML  = "<p class='success'>"+msg.success+"</p>";
	}

	PageScript.prototype.closePopup = function(popupCallback) {
		this.popupCallback=popupCallback //only for testing
		document.getElementById("PopupWindow_TitleDiv").innerHTML   = "";
		document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
		document.getElementById("PopupWindow_MessageDiv").innerHTML    = "";
		document.getElementById("PopupWindow_SuccessDiv").innerHTML = "";
		if (popupCallback) popupCallback();
		return "closePopup";
	}

	PageScript.prototype.uriCallback = function(status,text) {
		var data = JSON.parse(text);
		if (status==200) {
			self.QueryString.uris = data
			self.uribase = self.QueryString.uris.BACKEND_PATH
			var keygenform = document.getElementById("registration-keygenform")
			keygenform.action=self.QueryString.uris.BACKEND_PATH+"/v1/keygen"
			loc = '' + win.location
			if (loc.indexOf(self.QueryString.uris.SSL_LOGIN_BASE_URL) === 0) {
				self.ajaxget(self.QueryString.uris.SSL_LOGIN_BASE_URL+self.uribase+'/v1/ssl_login',pageScript.initCallback, true)
			}
			self.ajaxget("/v1/users/me", self.initCallback)
		}
		else self.displayMsg(self.processErrors(data));
	}
	PageScript.prototype.navigateToTheSection=function(section) {
		if (self.QueryString.section) self.doRedirect(self.QueryString.uris.BASE_URL+"/fiokom.html");
		else self.displayTheSection(section)
	}
	
	PageScript.prototype.displayTheSection=function(section) {
		self.hideAllSection();
		var lis=document.getElementsByClassName("navbar-nav")[0].getElementsByTagName("li");
		[].forEach.call( lis, function (e) { e.className=""; } );
		if (!section){
			if (self.isLoggedIn){

				self.unhideSection("my_account_section")
				document.getElementById("nav-bar-my_account").className="active"
				if (self.isAssurer) self.unhideSection("assurer_section")
			}
			else {
				self.unhideSection("login_section")
				document.getElementById("nav-bar-login").className="active"
			}
		}
		else {
			self.unhideSection(section+"_section")
			var navbar=document.getElementById("nav-bar-"+section)
			if (navbar) navbar.className="active";
		}
	}
	
}()
)