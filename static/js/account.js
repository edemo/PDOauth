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
			if (self.QueryString.section && self.QueryString.section=="email_verification"){
				if (self.QueryString.secret) self.verifyEmail()
			}
			self.ajaxget("/v1/users/me", self.initCallback)
			document.getElementById("digest_self_made_button").href=self.QueryString.uris.ANCHOR_URL
		}
		else self.displayMsg(self.processErrors(data));
	}
	
	PageScript.prototype.verifyEmail=function() {
		self.ajaxget( "/v1/verify_email/"+self.QueryString.secret, self.emailVerificationCallback )
	}	
	
	PageScript.prototype.emailVerificationCallback=function(status, text) {
		var message
		if (status==200) {
			message="Az email címed ellenőrzése sikerült."
		}
		else {
			message="Az email címed ellenőrzése <b>nem</b> sikerült.<p></p>"+text
		}
		document.getElementById("email_verification_message").innerHTML=message
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
	
	PageScript.prototype.setRegistrationMethode=function(methode){
		self.registrationMethode=methode;
		[].forEach.call( document.getElementById("registration-form-method-selector").getElementsByClassName("social"), function (e) { e.className=e.className.replace(" active",""); } );
		document.getElementById("registration-form-method-selector-"+methode).className+=" active"
		var heading
		switch (methode) {
			case "pw":
				heading="felhasználónév / jelszó"
				document.getElementById("registration-form-password-container").style.display="block";
				document.getElementById("registration-form-username-container").style.display="block";
			break;
			case "fb":
				heading="facebook fiókom"
				document.getElementById("registration-form-password-container").style.display="none";
				document.getElementById("registration-form-username-container").style.display="none";
				facebook.fbregister()
			break;
			case "ssl":
				heading="SSL kulcs"
				document.getElementById("registration-form-password-container").style.display="none";
				document.getElementById("registration-form-username-container").style.display="none";
			break;
		}
		document.getElementById("registration-form-method-heading").innerHTML="Regisztráció "+heading+" használatával";
	}

	PageScript.prototype.register = function(credentialType) {
		//
	    var identifier = document.getElementById("registration-form_identifier_input").value;
	    var secret = document.getElementById("registration-form_secret_input").value;
	    var email = document.getElementById("registration-form_email_input").value;
	    var digest = document.getElementById("registration-keygenform_digest_input").value;
	    text= {
	    	credentialType: credentialType,
	    	identifier: identifier,
	    	secret: secret,
	    	email: email,
	    	digest: digest
	    }
	    this.ajaxpost("/v1/register", text, this.myCallback)
	}
	
	PageScript.prototype.sslCallback=function() {
		console.log("sslCallback")
		response=document.getElementById("SSL").contentDocument.body.innerHTML
		if (response=="") self.doRedirect(self.QueryString.uris.SSL_LOGIN_BASE_URL+"fiokom.html")
		else {
			var msg
			if (data=JSON.parse(response)) {
				msg=self.processErrors(data)
			}
			else {
				msg.title="Szerverhiba"
				msg.error="response"
			}
			self.displayMsg(msg)
		}
	}	
	
	PageScript.prototype.doRegister=function() {
		if ( document.getElementById("registration-keygenform_confirmField").checked ) {
			switch (self.registrationMethode) {
				case "pw":
					self.register("password")
					break;
				case "fb":
					self.register("facebook")
					break;
				case "ssl":
					document.getElementById("SSL").onload=self.sslCallback;
					document.getElementById('registration-keygenform').submit();
					console.log("after submit")
//					self.doRedirect(self.QueryString.uris.SSL_LOGIN_BASE_URL+"fiokom.html")
					break;
			}
		}
		else self.displayMsg({title:"Felhasználási feltételek",error:"A regisztrácó feltétele a felhasználási feltételek elfogadása. Ha megértetted és elfogadod, kattints a regisztrálok gomb felett található a checkboxra "})
	}

	PageScript.prototype.sslLogin = function() {
		document.getElementById("SSL").onload=function(){win.location.reload()}
		document.getElementById("SSL").src=self.QueryString.uris.SSL_LOGIN_BASE_URL+self.uribase+'/v1/ssl_login'
	}
	
//Getdigest functions	
	PageScript.prototype.normalizeString = function(val) {
		var   accented="öüóőúéáűíÖÜÓŐÚÉÁŰÍ";
		var unaccented="ouooueauiouooueaui";
		var s = "";
		
		for (var i = 0, len = val.length; i < len; i++) {
		  c = val[i];
		  if(c.match('[abcdefghijklmnopqrstuvwxyz]')) {
		    s=s+c;
		  } else if(c.match('[ABCDEFGHIJKLMNOPQRSTUVXYZ]')) {
		    s=s+c.toLowerCase();
		  } else if(c.match('['+accented+']')) {
		    for (var j = 0, alen = accented.length; j <alen; j++) {
		      if(c.match(accented[j])) {
		        s=s+unaccented[j];
		      }
		    }
		  }
		}
		return s;
	}
	
	PageScript.prototype.digestGetter = function(formName) {
		var formName=formName
		var digestCallback
		
		digestCallback = function(status,text,xml) {
					console.log("cllaback "+formName)
					console.log("cllaback "+text)
			if (status==200) {
				var diegestInput=document.getElementById(formName + "_digest_input")
				diegestInput.value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
				$("#"+formName + "_digest_input").trigger('keyup');
				document.getElementById(formName + "_predigest_input").value = "";
				self.displayMsg({success:"<p class='success'>A titkosítás sikeres</p>"});
			} else {
				self.displayMsg({error:"<p class='warning'>" + text + "</p>"});
			}
		}
	
		this.getDigest = function() {
			console.log(formName)
			text = this.createXmlForAnchor(formName)
			if (text == null)
				return;
			console.log(text)
			http = self.ajaxBase(digestCallback);
			http.open("POST",self.QueryString.uris.ANCHOR_URL+"anchor",true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
	
		this.createXmlForAnchor = function(formName) {
			console.log(formName)
			personalId = document.getElementById(formName+"_predigest_input").value;
			motherValue = document.getElementById(formName+"_predigest_mothername").value;
			mothername = self.normalizeString(motherValue);
			if ( personalId == "") {
				self.displayMsg({error:"<p class='warning'>A személyi szám nincs megadva</p>"})
				return;
			}
			if ( mothername == "") {
				self.displayMsg({error:"<p class='warning'>Anyja neve nincs megadva</p>"})
				return;
			}
			return ("<request><id>"+personalId+"</id><mothername>"+mothername+"</mothername></request>");
		}
		
		return this
	}
	
	PageScript.prototype.convert_mothername = function(formName) {
		var inputElement = document.getElementById( formName+"_mothername");
		var outputElement = document.getElementById( formName+"_monitor");
		outputElement.innerHTML=document.getElementById( formName+"_input").value +' - '+ self.normalizeString(inputElement.value);
	}
	
	jQuery.each(jQuery('textarea[data-autoresize]'), function() {
		var offset = this.offsetHeight - this.clientHeight;
		var resizeTextarea = function(el) {
			jQuery(el).css('height', 'auto').css('height', el.scrollHeight + offset);
		};
		jQuery(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
	});
	
// assuring functions

	PageScript.prototype.byEmail = function() {
	    var email = document.getElementById("ByEmailForm_email_input").value;
		if (email=="") { self.displayMsg({title:"Hiba",error:"nem adtad meg az email címet"})}
		else {
			email = encodeURIComponent(email)
			this.ajaxget("/v1/user_by_email/"+email, this.myCallback)
		}
	}
	
	PageScript.prototype.addAssurance = function() {
	    digest = document.getElementById("assurancing_digest_input").value;
	    assurance = document.getElementById("assurance-giving_assurance_selector").value;
	    email = document.getElementById("ByEmailForm_email_input").value;
	    csrf_token = self.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	assurance: assurance,
	    	email: email,
	    	csrf_token: csrf_token
	    }
	    this.ajaxpost("/v1/add_assurance", text, this.myCallback)
	}
}()
)
