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
		self.ajaxget("/v1/users/me", self.initCallback)		
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		var data = JSON.parse(text);
		if (status != 200) {
			if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
			self.greating("The %s application needs to sign in with your ADA account")
			self.unhideSection("login_section")
		}
		else {
			self.isLoggedIn=true
			self.hideAllSection()
			if (self.neededAssurances) {
				var a=false;
				[].forEach.call(self.neededAssurances, function(assurance){
					if ( !data.assurances.hasOwnProperty(assurance)) {
						console.log(assurance)
						self.unhideSection(assurance+"_section")
						a=true;
					}
				})
				if (!a) {
					self.greating("The %s application will get the data below:")
					self.unhideSection("accept_section")
					self.ajaxget('/v1/getmyapps',self.myappsCallback)
				}
				else {
					self.greating("The %s application needs you have the assurances below")
				}
			}
			else self.ajaxget('/v1/getmyapps',self.myappsCallback)
		}
	}
				
	PageScript.prototype.greating = function (message){
		if (self.appDomain) {
			document.getElementById("greatings").innerHTML=_(message, '<b>'+self.appDomain+'</b>')
		}
	}
	
	PageScript.prototype.myappsCallback= function (status,text) {
		console.log('myappsCallback')
		if (status == 200 ) {
			self.myApps=JSON.parse(text)
			var a=false;
			for (i=0; i<self.myApps.length; i++){
				if (self.myApps[i].hostname==self.appDomain) {
					self.currentAppId=[i]
					if (!self.myApps[i].username) a=true
				}
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
	
	PageScript.prototype.displayMsg = function( msg ) {
		var text=(msg.error)?msg.error:""+(msg.success)?msg.success:""
		document.getElementById("message-container").innerHTML=text
		self.unhideSection("message-container")
	}
	
	PageScript.prototype.showSection=function(section) {
		self.hideAllSection()
		self.unhideSection(section)
	}
	PageScript.prototype.unhideSection=function(section) {
		document.getElementById(section).style.display="block";
	}
	
	PageScript.prototype.hideAllSection=function(){
		var a=document.getElementsByClassName("func");
		[].forEach.call( a, function (e) { e.style.display="none"; } );
	}
	
	PageScript.prototype.acceptGivingTheData=function(flag){
		if (flag){
			self.setAppCanEmailMe(self.currentAppId)
		}
		else {
			self.doRedirect(document.referrer)
		}
	}
	
	PageScript.prototype.setAppCanEmailMe=function(app){
		var value=document.getElementById("confirmForm_allowEmailToMe").checked
		var csrf_token = self.getCookie('csrf');
	    text= {
			canemail: value,
	    	appname: self.myApps[self.currentAppId].name,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/setappcanemail", text, self.myCallback)
	}
	
	PageScript.prototype.activateButton = function(buttonId, onclickFunc) {
		b=document.getElementById(buttonId)
		if (b) {
			b.className="";
			b.onclick=onclickFunc
		}
	}
	
	PageScript.prototype.changeHash = function() {
	    digest = document.getElementById("login_digest_input").value;
	    csrf_token = self.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/users/me/update_hash", text, self.changeHashCallback)
	}	
	
	PageScript.prototype.changeHashCallback = function(status,text) {
		switch (status) {
			case 500:
				self.displayMsg({title:_("Server failure"),error:text})
				break;
			case 200:
				win.location.reload()
			default:
				var data = JSON.parse(text);
				self.displayMsg(self.processErrors(data));	
		}
	}
}()
)