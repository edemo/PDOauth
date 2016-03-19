(function(){	
	var self;

	PageScript.prototype.page = "login";

	PageScript.prototype.main = function() {
		self=this.getThis()
		self.parseAppCallbackUrl();
		console.log(self.neededAssurances)
		console.log(self.appDomain)
		this.ajaxget("/adauris", this.uriCallback)
	}
	
	PageScript.prototype.parseAppCallbackUrl = function() {
		if (self.QueryString.next) {
			var a=decodeURIComponent(self.QueryString.next).split("?")
			var vars = self.QueryStringFunc('?'+a[1]);
			if (vars.redirect_uri) {
				var c=decodeURIComponent(vars.redirect_uri).split("?")
				self.appDomain=c[0].split('://')[1].split('/')[0]
				var b=self.QueryStringFunc('?'+c[1])
				if (b.need)	self.neededAssurances=b.need.split(',')
			}
		}
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
			else self.init_()
		}
		else self.displayMsg(self.processErrors(data));
	}
	
	PageScript.prototype.init_=function(){
		console.log("init_ called")
		if (self.QueryString.section && self.QueryString.section=="email_verification"){
			if (self.QueryString.secret) self.verifyEmail()
		}
		self.ajaxget("/v1/users/me", self.initCallback)		
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		var data = JSON.parse(text);
		if (status != 200) {
			if (self.appDomain) {
			document.getElementById("greatings").innerHTML='\
		<p>\
			<b>'+self.appDomain+'</b> '+_("application needs to sign in with your ADA account")+'\
		</p>'
			}
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
		console.log('myappsCallback')
		if (status == 200 ) {
			self.myApps=JSON.parse(text)
			var a=false;
			for (i=0; i<self.myApps.length; i++){
				if (self.myApps[i].hostname==self.appDomain && !self.myApps[i].username) a=true
			}
			if ( self.page=="login" && a){
				self.showSection("accept_section")
			}
			else {
				if( self.QueryString.next) {
					self.doRedirect(decodeURIComponent(self.QueryString.next))
				}
			}
		}
		else { 

			self.displayMsg(self.processErrors(text))
		}
	}
	PageScript.prototype.showSection=function(section) {
		self.hideAllSection()
		self.showSection(section)
	}
	PageScript.prototype.unhideSection=function(section) {
		document.getElementById(section).style.display="block";
	}
	PageScript.prototype.hideAllSection=function(){
		[].forEach.call( document.getElementsByClassName("func"), function (e) { e.style.display="none"; } );
	}
	
	PageScript.prototype.sslLogin = function() {
		document.getElementById("SSL").onload=function(){win.location.reload()}
		document.getElementById("SSL").src=self.QueryString.uris.SSL_LOGIN_BASE_URL+self.uribase+'/v1/ssl_login'
	}

}()
)