var QueryString = function () { //http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-url-parameter
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
        // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = pair[1];
        // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]], pair[1] ];
      query_string[pair[0]] = arr;
        // If third or later entry with this name
    } else {
      query_string[pair[0]].push(pair[1]);
    }
  } 
    return query_string;
} ();

var uribase="";

function PageScript(debug) {
	var self = this
	this.debug=debug

	PageScript.prototype.ajaxBase = function(callback) {
		var xmlhttp;
		if (window.XMLHttpRequest)
		  {// code for IE7+, Firefox, Chrome, Opera, Safari
		  xmlhttp=new XMLHttpRequest();
		  }
		else
		  {// code for IE6, IE5
		  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		  }
		xmlhttp.onreadystatechange=function()
		  {
		  if (xmlhttp.readyState==4)
		    {
		    	callback(xmlhttp.status,xmlhttp.responseText,xmlhttp.responseXML);
		    }
		  }
		return xmlhttp;
	}

	PageScript.prototype.ajaxpost = function(uri,data,callback) {
		xmlhttp = this.ajaxBase(callback);
		xmlhttp.open("POST",uribase+uri,true);
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		l = []
		for (key in data) {
			l.push(key +"=" +encodeURIComponent(data[key]));
		}
		t = l.join("&")
		console.log(t)
		xmlhttp.send(t);
	}

	PageScript.prototype.ajaxget = function(uri,callback) {
		xmlhttp = this.ajaxBase(callback)
		xmlhttp.open("GET",uribase+uri,true);
		xmlhttp.send();
	}

	PageScript.prototype.processErrors = function(data) {
			console.log(data)
			error="";
			messageMsg="";
			userdata="";
			if (data.message) messageMsg="<p>message</p>"+data.message;
			if (data.assurances) userdata="<p>success</p>"+self.parse_userdata(data);
			if (data.errors) {
				error = "<p>error</p><ul>";
				errs = data.errors;
				for ( err in errs ) error += "<li>"+ errs[err] +"</li>" ;
				error += "</ul>";
			}
			self.displayMsg(error,messageMsg,userdata);
	}
	
	PageScript.prototype.parse_userdata = function(data) {
		userdata = "<p><b>e-mail cím:</b> "+data.email+"</p>"
		userdata +="<p><b>felhasználó azonosító:</b> "+data.userid+"</p>"
		userdata +='<p><b>hash:</b></p><pre>'+data.hash+"</pre>"
		userdata +="<p><b>tanusítványok:</b></p>"
		userdata +="<ul>"
		for(ass in data.assurances) userdata += "<li>"+ass+"</li>"; 
		userdata +="</ul>"
		userdata +="<p><b>hitelesítési módok:</b></p>"
		userdata +="<ul>"
		for(i in data.credentials) userdata += "<li>"+data.credentials[i].credentialType+"</li>" ;
		userdata +="</ul>"
		return userdata;		
	}

	PageScript.prototype.myCallback = function(status, text) {
		var data = JSON.parse(text);
		if (status == 200) {
			if(QueryString.next) {
				window.location = decodeURIComponent(QueryString.next)
			}
		}
		self.processErrors(data)
		self.Init_Callback(status, text)
	}

	PageScript.prototype.passwordReset = function(myForm) {
		
	    secret = document.getElementById(myForm+"_secret_input").value;
	    password = document.getElementById(myForm+"_password_input").value;
	    this.ajaxpost("/v1/password_reset", {secret: secret, password: password}, this.myCallback)
	}
	
	PageScript.prototype.InitiatePasswordReset = function(myForm) {
		self.ajaxget("/v1/users/"+document.getElementById(myForm+"_email_input").value+"/passwordreset", self.myCallback)
	}
	
	PageScript.prototype.login = function() {
	    username = document.getElementById("LoginForm_username_input").value;
	    var onerror=false;
		document.getElementById("LoginForm_errorMsg").innerHTML="";
		if (username=="") {
			document.getElementById("LoginForm_errorMsg").innerHTML+="<p class='warning'>A felhasználónév nincs megadva</p>";
			onerror=true;
		}
	    password = document.getElementById("LoginForm_password_input").value;
	    if (password=="") {
			document.getElementById("LoginForm_errorMsg").innerHTML+="<p class='warning'>A jelszó nincs megadva</p>";
			onerror=true; 
		}
		if (onerror==true) return;
		else {
			username = encodeURIComponent(username);	
			password = encodeURIComponent(password);
			this.ajaxpost("/login", {credentialType: "password", identifier: username, secret: password}, this.myCallback)
			document.getElementById("DeRegisterForm_identifier_input").value=username;
			document.getElementById("DeRegisterForm_secret_input").value=password;
		}
	}

	PageScript.prototype.login_with_facebook = function(userId, accessToken) {
	    username = userId
	    password = encodeURIComponent(accessToken)
	    data = {
	    	credentialType: 'facebook',
	    	identifier: username,
	    	secret: password
	    }
	    this.ajaxpost("/login", data , this.myCallback)
		document.getElementById("DeRegisterForm_identifier_input").value=username;
		document.getElementById("DeRegisterForm_secret_input").value=password;
	}

	PageScript.prototype.byEmail = function() {
	    email = document.getElementById("ByEmailForm_email_input").value;
	    email = encodeURIComponent(email)
	    this.ajaxget("/v1/user_by_email/"+email, this.myCallback)
	}

	PageScript.prototype.logoutCallback = function(status, text) {
		self.myCallback(status,text);					// Ez ide minek, ha amúgy is újratöltünk
	    window.location = QueryString.uris.START_URL		
	}
	
	PageScript.prototype.logout = function() {
	    this.ajaxget("/logout", this.logoutCallback)
	}

	PageScript.prototype.uriCallback = function(status,text) {
		var data = JSON.parse(text);
		QueryString.uris = data
		self.processErrors(data)
		loc = '' + window.location
		if(loc.indexOf(QueryString.uris.SSL_LOGIN_BASE_URL) === 0) {
			console.log("ssl login");
			self.ajaxget(QueryString.uris.SSL_LOGIN_BASE_URL+'/ssl_login',pageScript.Init_Callback)
		}		
		
	}
	
	PageScript.prototype.sslLogin = function() {
		loc = '' +window.location
		newloc = loc.replace(QueryString.uris.BASE_URL, QueryString.uris.SSL_LOGIN_BASE_URL)
		console.log(newloc)
		window.location = newloc
	}

	PageScript.prototype.register = function() {
	    credentialType = document.getElementById("RegistrationForm_credentialType_input").value;
	    identifier = document.getElementById("RegistrationForm_identifier_input").value;
	    secret = document.getElementById("RegistrationForm_secret_input").value;
	    email = document.getElementById("RegistrationForm_email_input").value;
	    digest = document.getElementById("RegistrationForm_digest_input").value;
	    text= {
	    	credentialType: credentialType,
	    	identifier: identifier,
	    	secret: secret,
	    	email: email,
	    	digest: digest
	    }
	    this.ajaxpost("/v1/register", text, this.myCallback)
	}

	PageScript.prototype.add_facebook_credential = function(userId, accessToken) {
		text = {
			credentialType: "facebook",
			identifier: userId,
			secret: accessToken
		}
		self.ajaxpost("/v1/add_credential", text, function(status, text){
			var data = JSON.parse(text);
			console.log(data);
			if (status==200) {
				document.getElementById("me_Msg").innerHTML=self.parse_userdata(data);
			}
		})
	}
	
	PageScript.prototype.register_with_facebook = function(userId, accessToken, email) {
	    username = userId;
	    password = accessToken;
	    text = {
	    	credentialType: "facebook",
	    	identifier: username,
	    	secret: password,
	    	email: email
	    }
	    this.ajaxpost("/v1/register", text, this.myCallback)
	}
	
	PageScript.prototype.getCookie = function(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
	    }
	    return "";
	} 
	
	PageScript.prototype.addAssurance = function() {
	    digest = document.getElementById("AddAssuranceForm_digest_input").value;
	    assurance = document.getElementById("AddAssuranceForm_assurance_input").value;
	    email = document.getElementById("AddAssuranceForm_email_input").value;
	    csrf_token = this.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	assurance: assurance,
	    	email: email,
	    	csrf_token: csrf_token
	    }
	    this.ajaxpost("/v1/add_assurance", text, this.myCallback)
	}

	PageScript.prototype.hashCallback = function(status,text) {
		if (status==200) { 
			self.ajaxget('/v1/users/me',function(status, text){
				if (status==200) {
					var data = JSON.parse(text);
					document.getElementById("me_Msg").innerHTML=self.parse_userdata(data);	
				}
			});
		}
		else {
			var data = JSON.parse(text);
			document.getElementById("ChangeHashForm_ErrorMsg").innerHTML='<p class="warning">'+data.errors+'</p>';	
		}
	}
	
	PageScript.prototype.InitiateResendRegistrationEmail = function() {
		document.getElementById("InitiateResendRegistrationEmail_ErrorMsg").innerHTML='<p class="warning">Ez a funkció sajnos még nem működik</p>';	
		}
	
	PageScript.prototype.changeHash = function() {
		document.getElementById("ChangeHashForm_ErrorMsg").innerHTML="";
	    digest = document.getElementById("ChangeHashForm_digest_input").value;
	    csrf_token = this.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/users/me/update_hash", text, this.hashCallback)
	}
	
	PageScript.prototype.digestGetter = function(formName) {
		self.formName = formName
		self.idCallback = function(status,text, xml) {
			if (status==200) {
		    	document.getElementById(self.formName + "_digest_input").value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
				document.getElementById(self.formName + "_predigest_input").value = "";
				document.getElementById(self.formName + "_errorMsg").innerHTML="<p class='warning'>A titkosítás sikeres</p>"
			} else {
				document.getElementById(self.formName + "_errorMsg").innerHTML="<p class='warning'>" + text + "</p>"
			}
		}
	
		self.getDigest = function() {
			personalId = document.getElementById(this.formName+"_predigest_input").value;
			if ( personalId == "") {
				document.getElementById(self.formName + "_errorMsg").innerHTML="<p class='warning'>A személyi szám nincs megadva</p>"
				return;
			}
			text = "<id>"+personalId+"</id>"
			http = this.ajaxBase(this.idCallback);
			http.open("POST",'https://anchor.edemokraciagep.org/anchor',true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
		return self
	}

	PageScript.prototype.loadjs = function(src) {
	    var fileref=document.createElement('script')
	    fileref.setAttribute("type","text/javascript")
	    fileref.setAttribute("src", src)
	    document.getElementsByTagName("head")[0].appendChild(fileref)
	}
	
	PageScript.prototype.unittest = function() {
		this.loadjs("tests.js")
	}
	
	PageScript.prototype.changeEmailAddress = function() {
	    email = document.getElementById("ChangeEmailAddressForm_email_input").value;
		if (email=="") document.getElementById("ChangeEmailAddressForm_ErrorMsg").innerHTML="<p class='warning'>Nincs megadva érvényes e-mail cím</p>";
		else document.getElementById("ChangeEmailAddressForm_ErrorMsg").innerHTML="<p class='warning'>Ez a funkció sajnos még nem elérhető</p>";
	}
	
	PageScript.prototype.Init_Callback = function(status, text) {
		console.log('Init_Callback');
		console.log(JSON.parse(text));
		var data = JSON.parse(text);
		if (status != 200) {
			self.menuHandler("login").menuActivate();
			self.menuHandler("account").menuHide();
			self.menuHandler("assurer").menuHide();
			self.menuHandler("registration").menuUnhide();
			self.processErrors(data);
		}
		else {
			if (!self.activeButton)	self.menuHandler("account").menuActivate();
			else {
				var a=["login", "register"];
				if ( a.indexOf(self.activeButtonName) > -1 ) self.menuHandler("account").menuActivate();
			}
			self.menuHandler("login").menuHide();
			self.menuHandler("registration").menuHide();
			if (data.assurances) {
				document.getElementById("me_Msg").innerHTML=self.parse_userdata(data);
				if (data.assurances.emailverification) document.getElementById("InitiateResendRegistrationEmail_Container").style.display = 'none';
				if (data.email) {
					document.getElementById("AddSslCredentialForm_email_input").value=data.email;
					document.getElementById("PasswordResetInitiateForm_email_input").value=data.email;
				}
				if (!(data.assurances.assurer)) self.menuHandler("assurer").menuHide();
				else self.menuHandler("assurer").menuUnhide();
			}
			self.fill_RemoveCredentialContainer(data);
		}
	}
	
	PageScript.prototype.fill_RemoveCredentialContainer = function(data) {
		var container = '<div class="msg">';
		var i=0;
		for(CR in data.credentials) {
			container += '<div id="RemoveCredential_'+i+'">';
			container += '<table class="content_" "><tr><td width="25%"><p id="RemoveCredential_'+i+'_credentialType">';
			container += data.credentials[CR].credentialType+'</p></td>';
			container += '<td style="max-width: 100px;"><pre id="RemoveCredential_'+i+'_identifier">'
			container += data.credentials[CR].identifier+'</pre></td>';
			container += '<td width="10%"><div><button class="button" type="button" id="RemoveCredential_'+i+'_button" ';
			container += 'onclick="javascript:pageScript.RemoveCredential(';
			container += "'RemoveCredential_"+i+"').doRemove()";
			container += '">Törlöm</button></div></td>';
			container += '</tr></table></div>' ;
			i++;
		}
		container += "</div>";
		document.getElementById("Remove_Credential_Container").innerHTML=container;
	}
	
	PageScript.prototype.RemoveCredential = function(formName) {
		self.formName = formName
		self.rmCredential_Callback = function(status,text) {
			if (status==200) {
		    	document.getElementById(self.formName).innerHTML = "<p class='success'>Ezt a hitelesítési módot töröltük</p>";
				self.displayMsg('','',"<p>"+text+"</p><p class='success'>Ezt a hitelesítési módot töröltük</p>")
			} else {
				var data=JSON.parse(text);
				self.displayMsg("<p class='warning'>" + data.errors + "</p>","","")
			}
		}
	
		self.doRemove = function() {
			credentialType = document.getElementById(this.formName+"_credentialType").innerHTML;
			identifier = document.getElementById(this.formName+"_identifier").innerHTML;
			text = {
				credentialType: credentialType,
				identifier: identifier
			}
			this.ajaxpost("/v1/remove_credential", text, this.rmCredential_Callback);
		}

		return self
	}

	
	PageScript.prototype.addGoogleCredential = function(){
		document.getElementById("AddCredentialForm_ErrorMsg").innerHTML="<p class='warning'>Ez a funkció sajnos még nem működik</p>";
	}
	
	PageScript.prototype.GoogleLogin = function(){
		document.getElementById("Login-ErrorMsg").innerHTML="<p class='warning'>A google bejelentkezés funkció sajnos még nem működik</p>";
	}
	
	PageScript.prototype.GoogleRegister = function(){
		self.displayMsg("<p class='warning'>A google bejelentkezés funkció sajnos még nem működik</p>",'','');
	}
	
	PageScript.prototype.TwitterLogin = function(){
		document.getElementById("Login-ErrorMsg").innerHTML="<p class='warning'>A twitter bejelentkezés funkció sajnos még nem működik</p>";
	}
	
	PageScript.prototype.addPassowrdCredential = function(){
		identifier=document.getElementById("AddPasswordCredentialForm_username_input").value;
		secret=document.getElementById("AddPasswordCredentialForm_password_input").value;
		self.addCredential("password", identifier, secret);
	}
	
	PageScript.prototype.addCredential = function(credentialType, identifier, secret) {
		text = {
			credentialType: credentialType,
			identifier: identifier,
			secret: secret
		}
		self.ajaxpost("/v1/add_credential", text, function(status,text){
			var data = JSON.parse(text);
			console.log(data)
			if (status != 200) {
				document.getElementById("AddCredentialForm_ErrorMsg").innerHTML="<p class='warning'>"+data.errors+"</p>";
			}
			else {
				document.getElementById("AddCredentialForm_ErrorMsg").innerHTML="<p class='warning'>Hitelesítési mód sikeresen hozzáadva</p>";
				self.ajaxget("/v1/users/me", self.Init_Callback);
			}
		})
	}	
	
	PageScript.prototype.deRegister = function() {
		self.ajaxget("/v1/users/me", function(status, text){
				if (status != 200) {
					document.getElementById("DeRegisterForm_ErrorMsg").innerHTML="<p class='warning'>Hibás autentikáció</p>";
					return;
				}
				else {
					var data = JSON.parse(text);
					text = {
						csrf_token: self.getCookie("csrf"),
						credentialType: "password",
						identifier: document.getElementById("DeRegisterForm_identifier_input").value,
						secret: document.getElementById("DeRegisterForm_secret_input").value
					}
					self.ajaxpost("/deregister", text, function(status, text){
						var data = JSON.parse(text);
						if (status != 200) document.getElementById("DeRegisterForm_ErrorMsg").innerHTML="<p class='warning'>"+data.errors+"</p>";
						else document.getElementById("DeRegisterForm_ErrorMsg").innerHTML="<p class='warning'>A fiók törlése megtörtént.</p>";
					})
				}
			})
		
	}
	
	PageScript.prototype.displayMsg = function(errorMsg,messageMsg,successMsg) {
		if (errorMsg+messageMsg+successMsg=="") return;
		document.getElementById("popup").style.display  = "flex";
		document.getElementById("errorMsg").innerHTML   = "<p class='warning'>"+errorMsg+"</p>";
		document.getElementById("message").innerHTML    = "<p class='message'>"+messageMsg+"</p>";
		document.getElementById("successMsg").innerHTML = "<p class='success'>"+successMsg+"</p>";
		document.getElementById('fade').style.display='block';
		document.getElementById('fade').style.filter='alpha(opacity=50)';
		document.getElementById('fade').style.opacity='0.5';
	}
	
	PageScript.prototype.closePopup = function() {
		document.getElementById("errorMsg").innerHTML   = "";
		document.getElementById("message").innerHTML    = "";
		document.getElementById("successMsg").innerHTML = "";
		document.getElementById('popup').style.display='none';
		document.getElementById('fade').style.display='none';
	}
	
	PageScript.prototype.menuHandler = function(menu_item) {
		self.menuName=menu_item;
		self.menuButton=document.getElementById(self.menuName+"-menu");
		self.menuTab=document.getElementById("tab-content-"+self.menuName);
		if (typeof(theMenu=document.getElementsByClassName("active-menu")[0])!="undefined") {
			self.activeButton=theMenu;
			self.activeButtonName=self.activeButton.id.split("-")[0];
			self.activeTab=document.getElementById("tab-content-"+self.activeButtonName);
		}
		
		self.menuActivate = function() {
			if (self.activeButton) { 
				self.activeButton.className="";
				self.activeTab.style.display="none";
			}
			self.menuButton.style.display="block";
			self.menuButton.className="active-menu";
			self.menuTab.style.display="block";
		}

		self.menuDeactivate = function() {
			self.menuButton.className="";
			self.menuTab.style.display="none";
		}
		
		self.menuHide = function() {
			self.menuButton.style.display="none";
		}
		
		self.menuUnhide = function() {
			self.menuButton.style.display="block";
		}
		console.log(self);
		return self;
	}

	PageScript.prototype.main = function() {
		this.ajaxget("/uris", this.uriCallback)
		this.ajaxget("/v1/users/me", this.Init_Callback)
		if (QueryString.secret) {
			document.getElementById("PasswordResetForm_secret_input").value=QueryString.secret
			document.getElementById("PasswordResetForm_OnLoginTab_secret_input").value=QueryString.secret
		}
		
	}

}

pageScript = new PageScript();
