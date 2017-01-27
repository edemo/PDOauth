(function(){	
	var self;

	PageScript.prototype.page = "login";

	PageScript.prototype.main = function() {
		self=this.getThis()
		self.parseAppCallbackUrl();
		self.dataGivingAccepted=false;
		console.log(self.neededAssurances)
		console.log(self.appDomain)
		self.ajaxget("/adauris", self.callback(self.commonInit), true )
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
	
	PageScript.prototype.initialise = function() {
		// redirect to official account page if callback uri is missing
		if (!self.appDomain) self.doRedirect(self.QueryString.uris.START_URL)
		self.ajaxget("locale/hu.json",self.callback(self.initGettext),true)
	}
	
	PageScript.prototype.init_=function(){
		console.log("init_ called")
		self.ajaxget("/v1/users/me", self.callback(self.userIsLoggedIn, self.userNotLoggedIn))		
	}
	
	PageScript.prototype.userNotLoggedIn = function(text) {
		var data = JSON.parse(text);
		if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
		else {
			self.greating("The %s application needs to sign in with your ADA account")
			if (self.QueryString.section && self.QueryString.section=="registration") self.unhideSection("register_section")
			else self.unhideSection("login_section")
		}
		window.traces.push('loginpage')
	}
	
	PageScript.prototype.userIsLoggedIn = function(text) {
		var data = JSON.parse(text);
		self.isLoggedIn=true
		self.hideAllSection()
		if (self.neededAssurances) {
			var missing=false;
			[].forEach.call(self.neededAssurances, function(assurance){
				if ( !data.assurances.hasOwnProperty(assurance)) {
					self.unhideAssuranceSection(assurance,false)
					missing=true;
					if (self.neededAssurances.length==1) self.showForm(assurance)
				}
				else self.unhideAssuranceSection(assurance,true)
			})
			if (missing) {
				self.greating("The %s application needs you have the assurances below")
				return
			}
		}
		self.ajaxget('/v1/getmyapps',self.callback(self.myappsCallback))
		if ( self.dataGivingAccepted ) {
			if( self.QueryString.next) {
				self.doRedirect(decodeURIComponent(self.QueryString.next))
			}
		}
		window.traces.push('userIsLoggedIn')
	}
	
	PageScript.prototype.finishRegistration = function (text) {
		console.log('finis registering')
		self.myappsCallback(text)
		self.dataGivingAccepted=true
		var value=document.getElementById("registration-form_allowEmailToMe").checked
		self.setAppCanEmailMe(self.currentAppId, value, self.init_)
	}
	
	PageScript.prototype.myappsCallback= function (text) {
		console.log('myappsCallback')
		self.aps=JSON.parse(text)
		for (i=0; i<self.aps.length; i++){
			if (self.aps[i].hostname==self.appDomain) {
				self.currentAppId=i
				if (self.aps[i].username) self.dataGivingAccepted=true
			}
		}
		if ( !self.dataGivingAccepted ){
			self.greating("The %s application will get the data below:")
			self.showSection("accept_section")
		}
		else {
			if ( self.QueryString.next) {
				self.doRedirect(decodeURIComponent(self.QueryString.next))
			}
		}
		window.traces.push("myApps")
	}
	
	PageScript.prototype.unhideAssuranceSection= function(assurance,given) {
		document.getElementById(assurance+"_ok").style.display=(given)?"block":"none"
		document.getElementById(assurance+"_button").style.display=(given)?"none":"block"
		document.getElementById(assurance+"_header").style.display="block"
		document.getElementById(assurance+"_input").style.display="none"
		self.unhideSection(assurance+"_section")
	}
				
	PageScript.prototype.greating = function (message){
		if (self.appDomain) {
			document.getElementById("greatings").innerHTML=_(message, '<b>'+self.appDomain+'</b>')
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
		if (section=="register_section" && self.neededAssurances.indexOf('hashgiven')!=-1) self.unhideSection("registration-form-getdigest_input")
	}
	
	PageScript.prototype.acceptGivingTheData=function(flag){
		if (flag){
			self.dataGivingAccepted=true
			var value=document.getElementById("confirmForm_allowEmailToMe").checked
			self.setAppCanEmailMe(self.currentAppId, value, self.init_)
		}
		else {
			self.doRedirect(document.referrer)
		}
	}

	PageScript.prototype.textareaOnKeyup = function(textarea) {
		if (textarea) {
			if (textarea.value.length==128) self.activateButton('code-generation-input_button',self.changeHash);
			else self.deactivateButton('code-generation-input_button');
		}
	}

	PageScript.prototype.deactivateButton = function(buttonId) {
		b=document.getElementById(buttonId)
		if (b) {
			b.className+=" inactive";
			b.onclick=function(){return}
		}		
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
	    data= {
	    	digest: digest,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost( "/v1/users/me/update_hash", data, self.callback(self.hashIsUpdated) )
	}	
	
	PageScript.prototype.hashIsUpdated = function(text) {
		self.hideAllSection()
		self.init_()
		window.traces.push("hashIsUpdated")
	}
	
	PageScript.prototype.showForm = function(formName) {
		document.getElementById(formName+"_header").style.display="none";
		document.getElementById(formName+"_input").style.display="block";
	}
	
	PageScript.prototype.hideForm = function(formName) {
		document.getElementById(formName+"_header").style.display="block";
		document.getElementById(formName+"_input").style.display="none";
	}

}()
)
