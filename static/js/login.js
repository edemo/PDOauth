(function(){	
	var self;
	PageScript.prototype.page = "login";

	PageScript.prototype.main = function() {
		self=this.getThis()
		this.ajaxget("/adauris", this.uriCallback)
	}

	PageScript.prototype.uriCallback = function(status,text) {
		var data = JSON.parse(text);
		if (status==200) {
			self.QueryString.uris = data
			self.uribase = self.QueryString.uris.BACKEND_PATH
			var keygenform = document.getElementById("registration-keygenform")
			keygenform.action=self.QueryString.uris.BACKEND_PATH+"/v1/keygen"
			loc = '' + win.location
			document.getElementById("digest_self_made_button").href=self.QueryString.uris.ANCHOR_URL
			if (!Gettext.isAllPoLoaded) Gettext.outerStuff.push(self.init_);
			else self.init()
		}
		else self.displayMsg(self.processErrors(data));
	}
	
	PageScript.prototype.init_=function(){
		console.log("init_ called by gettext")
		if (self.QueryString.section && self.QueryString.section=="email_verification"){
			if (self.QueryString.secret) self.verifyEmail()
		}
		self.ajaxget("/v1/users/me", self.initCallback)		
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		var data = JSON.parse(text);
		if (status != 200) {
			if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
		}
		else {
			self.ajaxget('/v1/getmyapps',self.myappsCallback)
			self.isLoggedIn=true
		}	
	}
	
	PageScript.prototype.displayMsg = function( msg ) {
		var text=(msg.error)?msg.error:""+(msg.success)?msg.success:""
		document.getElementById("message-container").innerHTML=text
	}
	
	PageScript.prototype.myappsCallback= function (status,text) {
			if (status == 200 ) {
				if( self.page=="login"){
					if( self.QueryString.next) {
						self.doRedirect(decodeURIComponent(self.QueryString.next))
					}
				}
			}
		else self.displayMsg(self.processErrors(text))
	}
	PageScript.prototype.sslLogin = function() {
		document.getElementById("SSL").onload=function(){win.location.reload()}
		document.getElementById("SSL").src=self.QueryString.uris.SSL_LOGIN_BASE_URL+self.uribase+'/v1/ssl_login'
	}

}()
)