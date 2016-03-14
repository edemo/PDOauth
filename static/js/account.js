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
			document.getElementById("digest_self_made_button").href=self.QueryString.uris.ANCHOR_URL
			if (!Gettext.allPoIsLoaded) Gettext.outerStuff.push(self.init_);
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
	
	PageScript.prototype.verifyEmail=function() {
		self.ajaxget( "/v1/verify_email/"+self.QueryString.secret, self.emailVerificationCallback )
	}	
	
	PageScript.prototype.emailVerificationCallback=function(status, text) {
		var message
		if (status==200) {
			message=_("Your email validation was succesfull.")
		}
		else {
			data=JSON.parse(text);
			message=_("Your email validation <b>failed</b>.<br/>The servers response: ")+_(data.errors[0])
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
				heading=_("email address and/or username / password")
				document.getElementById("registration-form-password-container").style.display="block";
				document.getElementById("registration-form-username-container").style.display="block";
			break;
			case "fb":
				heading=_("my facebook account")
				document.getElementById("registration-form-password-container").style.display="none";
				document.getElementById("registration-form-username-container").style.display="none";
				facebook.fbregister()
			break;
			case "ssl":
				heading=_("SSL certificate")
				document.getElementById("registration-form-password-container").style.display="none";
				document.getElementById("registration-form-username-container").style.display="none";
			break;
		}
		document.getElementById("registration-form-method-heading").innerHTML=_("Registration with {0}",heading);
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
	
	PageScript.prototype.sslRegisterCallback= function(){
		if (self.sslCallback()) self.sslLogin();
	}

	PageScript.prototype.addSslCredentialCallback= function(){
		if (self.sslCallback()) self.getMe();
	}

	PageScript.prototype.sslCallback=function() {
		console.log("sslCallback")
		response=document.getElementById("SSL").contentDocument.body.innerHTML
		if (response!="")  {
			var msg
			if (data=JSON.parse(response)) {
				msg=self.processErrors(data)
			}
			else {
				msg.title=_("Server error occured")
				msg.error=response
			}
			self.displayMsg(msg)
			return false
		}
		else return true
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
					document.getElementById("SSL").onload=self.sslRegisterCallback;
					document.getElementById('registration-keygenform').submit();
					console.log("after submit")
//					self.doRedirect(self.QueryString.uris.SSL_LOGIN_BASE_URL+"fiokom.html")
					break;
			}
		}
		else self.displayMsg({title:_("Acceptance is missing"),error:_("Text for missing accaptance of term of use")})
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
			var diegestInput=document.getElementById(formName + "_digest_input")
			if (status==200) {
				diegestInput.value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
				$("#"+formName + "_digest_input").trigger('keyup');
				document.getElementById(formName + "_predigest_input").value = "";
				if (formName=="assurancing") {
					var messageBox=document.getElementById("assurance-giving_message")
					messageBox.innerHTML=_("The Secret Hash is given for assuring")
					messageBox.className="given"
					document.getElementById("assurance-giving_submit-button").className=""
				}
			} else {
				self.displayMsg({title:_("Error message"),error: text});
				diegestInput.value =""
				if (formName=="assurancing") {
					var messageBox=document.getElementById("assurance-giving_message")
					messageBox.innerHTML=_("The Secret Hash isn't given yet")
					messageBox.className="missing"
					document.getElementById("assurance-giving_submit-button").className="inactive"
				}
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
				self.displayMsg({title:_('Missing data'), error:_("Personal identifier is missing")})
				return;
			}
			if ( mothername == "") {
				self.displayMsg({title:_('Missing data'), error:_("Mother's name is missing")})
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

/*
********************************
**    Adding credencials      **
********************************
*/	
	PageScript.prototype.addSslCredential = function(data) {
		document.getElementById("SSL").onload=self.addSslCredentialCallback;
		document.getElementById('add-ssl-credential-keygenform').submit();
	}
	
/*
********************************
**      Change settings       **
********************************
*/

	PageScript.prototype.changeHash = function() {
	    digest = document.getElementById("change-hash-form_digest_input").value;
	    csrf_token = this.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/users/me/update_hash", text, this.hashCallback)
	}	
	PageScript.prototype.viewChangeHashForm = function() {
		document.getElementById("change-hash-form_hash-changer").style.display="table-row";
		document.getElementById("change-hash-form_hash-container").style.display="none";
	}
	
	PageScript.prototype.viewChangeHashContainer = function() {
		document.getElementById("change-hash-form_hash-changer").style.display="none";
		document.getElementById("change-hash-form_hash-container").style.display="table-row";
	}
	
/*
********************************
** My account section content **
********************************

/***** Settings tab *****/
	PageScript.prototype.parseSettings = function(data) {

		var sslForm='\
		<form target="ssl" id="add-ssl-credential-keygenform" method="post" action="/ada/v1/keygen" enctype="application/x-x509-user-cert">\
			<keygen name="pubkey" challenge="123456789" keytype="RSA" style="display: none"></keygen>\
			<input id="add-ssl-credential_createuser_input" type="checkbox" name="createUser" value="true" style="display: none">\
			<input type="text" id="add-ssl-credential_email_input"  name="email" value="'+data.email+'" style="display: none">\
		</form>'
				
		var result = '\
		<table>\
			<tr>\
				<td nowrap><b>'+_('Email address:')+'</b></td>\
				<td id="email-change">\
					<input type="text" value="'+data.email+'" id="userdata_editform_email_input">\
				</td>\
				<td><a onclick="javascript:pageScript.myAccountItem(\"email-change\").edit" class="btn btn_ fa fa-edit"></a></td>\
			</tr>\
			<tr id="change-hash-form_hash-container">\
				<td nowrap><b>'+_("The Secret Hash:")+'</b></td>\
				<td>\
					<pre id="change-hash-form_digest-pre"><code>'+((data.hash)?data.hash:"")+'</code></pre>\
				</td>\
				<td>\
					<a onclick="javascript:pageScript.viewChangeHashForm()" class="btn btn_ fa fa-edit"></a>\
				</td>\
			</tr>\
			<tr id="change-hash-form_hash-changer" style="display: none;">\
				<td nowrap><b>'+_("The Secret Hash:")+'</b></td>\
				<td>\
					<p><b>'+_("If you change your Secret Hash, all of your assurences will be deleted!")+'</b></p>\
					<textarea data-autoresize class="digest" type="text" id="change-hash-form_digest_input""></textarea>\
					<button class="button" type="button" onclick="javascript:document.getElementById(\'change-hash-form_code-generation-input\').style.display=\'block\'">'+_("Let's make it here")+'</button>\
					<a id="digest_self_made_button" href="'+self.QueryString.uris.ANCHOR_URL+'" target="_blank">\
						<button class="button" type="button" onclick="javascript:document.getElementById(\'code-generation-input\').style.display=\'none\'">'+_("I make it myself")+'</button>\
					</a>\
					<div id="change-hash-form_code-generation-input" class="form">\
						<div class="bordered">\
							<label for="input">'+_("Personal identifier")+':</label>\
							<input type="text" placeholder="" id="change-hash-form_predigest_input" onkeyup="pageScript.convert_mothername(\'change-hash-form_predigest\')">\
							<label for="mothername">'+_("Mother's name")+':</label>\
							<input type="text" placeholder="" id="change-hash-form_predigest_mothername" onkeyup="pageScript.convert_mothername(\'change-hash-form_predigest\')">\
							<button type="button" onclick="pageScript.digestGetter(\'change-hash-form\').getDigest()">'+_("Generate")+'</button>\
							<div class="monitor" id="change-hash-form_predigest_monitor"></div>\
						</div>\
					</div>\
				</td>\
				<td>\
					<a onclick="javascript:pageScript.myAccountItem(\"email-change\").edit" class="btn btn_ fa fa-save" title="'+_("save")+'"></a>\
					<a onclick="javascript:pageScript.viewChangeHashContainer()" class="btn btn_ fa fa-times" title="'+_("cancel")+'"></a>\
				</td>\
			</tr>\
		</table>\
		<h4><b>'+_("My credentials")+'</b></h4>\
		<table class="multiheader">';
		var c={	pw:[_("Password"),"password","pageScript.addPasswordCredential()",true],
				ssl:[_("SSL certificate"),"certificate","pageScript.addSslCredential()",true],
				fb:["Facebook","facebook","facebook.add_fb_credential()",false],
				git:["Github","github","pageScript.addGithubCredential()",false],
				tw:["Twitter","twitter","pageScript.addTwitterCredential()",false],
				go:["Google+","google","pageScript.addGoogleCredential()",false]
				};
		var credential_list = ""
		for( var i in c) {
			credential_list = ""
			for(var j=0; j<data.credentials.length; j++) {
				if (data.credentials[j].credentialType==c[i][1]) {
					credential_list += '\
			<tr>\
				<td  ><pre class="credential-item" id="Credential-Item-'+j+'_identifier">'+data.credentials[j].identifier+'</pre></td>\
				<td>\
					<a onclick="javascript:pageScript.RemoveCredential(\'Credential-Item-'+j+'\').doRemove(\''+c[i][1]+'\')" class="btn btn_ fa fa-trash"></a>\
				</td>\
			</tr>'
				}
			}
			credential_header='\
			<tr id="'+i+'-credential-list">\
				<th>'+c[i][0]+'</th>\
				<th>'
			if (c[i][3] || credential_list==''  ) {
				credential_header +='\
					<a onclick="javascript:'+c[i][2]+'" class="btn fa fa-plus"></a>';
			}
			credential_header +='\
				</th>\
			</tr>'
			result+=credential_header+credential_list
		}
		result +='\
		</table>'+sslForm
		return result;		
	}	
}()
)
