QueryStringFunc = function (win) { //http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-url-parameter
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  win=win || window 			// to be testable
  var query_string = {};
  var query = win.location.search.substring(1);
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
};


function PageScript(test) {
	var self = this
	test=test || { debug: false, uribase: "" }
	this.debug=test.debug
	win = test.win || window;
    this.QueryString = QueryStringFunc();
    self.uribase=test.uribase;
	this.isLoggedIn=false;
	this.isAssurer=false;
	this.registrationMethode="pw";
	
	PageScript.prototype.setRegistrationMethode=function(methode){
		self.registrationMethode=methode;
		[].forEach.call( document.getElementById("registration-form-method-selector").getElementsByClassName("social"), function (e) {e.className=e.className.replace(" active",""); console.log(e.className) } );
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
			break;
			case "ssl":
				heading="SSL kulcs"
				document.getElementById("registration-form-password-container").style.display="none";
				document.getElementById("registration-form-username-container").style.display="none";
			break;
		}
		document.getElementById("registration-form-method-heading").innerHTML="Regisztráció "+heading+" használatával";
	}
	
	PageScript.prototype.getThis=function() {
		return this
	}
	PageScript.prototype.ajaxBase = function(callback) {
		var xmlhttp;
		if (win.XMLHttpRequest)
		  {// code for IE7+, Firefox, Chrome, Opera, Safari
		  xmlhttp = new win.XMLHttpRequest();
//		  xmlhttp.oName="XMLHttpRequest"; // for testing
		  }
		else
		  {// code for IE6, IE5
		  xmlhttp = new win.ActiveXObject("Microsoft.XMLHTTP");
//		  xmlhttp.oName="ActiveXObject";   // for testing
		  }
		xmlhttp.callback=callback // for testing
		xmlhttp.onreadystatechange=function()
		  {
		  if (xmlhttp.readyState==4)
		    {
		    	callback(xmlhttp.status,xmlhttp.responseText,xmlhttp.responseXML);
		    }
		  }
		return xmlhttp;
	}

	PageScript.prototype.ajaxpost = function( uri, data, callback ) {
		xmlhttp = this.ajaxBase( callback );
		xmlhttp.open( "POST", self.uribase + uri, true );
		xmlhttp.setRequestHeader( "Content-type","application/x-www-form-urlencoded" );
		l = []
		for (key in data) l.push( key + "=" + encodeURIComponent( data[key] ) ); 
		var dataString = l.join("&")
		console.log(uri+' - '+data)
		xmlhttp.send( dataString );
	}

	PageScript.prototype.ajaxget = function( uri, callback, direct) {
		xmlhttp = this.ajaxBase( callback )
		if (direct) {
			theUri = uri;
		} else {
			theUri = self.uribase + uri;
		}
console.log(theUri)
		xmlhttp.open( "GET", theUri , true);
		xmlhttp.send();
	}

	PageScript.prototype.processErrors = function(data) {
			var msg = {};
			if (data.message) {
				msg.title="Szerverüzenet";
				msg.message="<p>message</p><p>"+data.message+"</p>";
			}
			if (data.assurances) {
				msg.title="A felhasználó adatai";
				msg.success=self.parseUserdata(data);
			}
			if (data.errors) {
				msg.title = "Hibaüzenet"
				msg.error = "<ul>";
				errs = data.errors;
				for ( err in errs ) msg.error += "<li>"+ errs[err] +"</li>" ;
				msg.error += "</ul>";
			}
			return msg;
	}
	
	PageScript.prototype.parseSettings = function(data) {
		var result = '\
		<table>\
			<tr>\
				<td nowrap><b>E-mail cím:</b></td>\
				<td id="email-change">\
					<input type="text" value="'+data.email+'" id="userdata_editform_email_input">\
					</td>\
				<td><a onclick="javascript:pageScript.myAccountItem(\"email-change\").edit" class="btn fa fa-edit"></a></td>\
			</tr>\
			<tr>\
				<td nowrap><b>Titkós kód</b></td>\
				<td>\
					<pre><code>'+((data.hash)?data.hash:"")+'</code></pre>\
				</td>\
				<td>\
					<a onclick="javascript:pageScript.myAccountItem(\"email-change\").edit" class="btn fa fa-edit"></a>\
				</td>\
		</table>\
		<h4><b>Hitelesítési módjaim:</b></h4>\
		<table>';
		var c={	pw:["Jelszavas","password"],
				fb:["Facebook","facebook"],
				ssl:["SSL kulcs","certificate"] 
				};
		for( var i in c) {
					result +='\
			<tr id="'+i+'-credential-list">\
				<th>'+c[i][0]+'</th>\
				<th>\
					<a onclick="javascript:pageScript.addItem(\"'+i+'\").edit" class="btn fa fa-plus"></a>\
				</th>\
			</tr>'
			for(var j=0; j<data.credentials.length; j++) {
				console.log(c[i][1]+' - '+data.credentials[j].credentialType)
				if (data.credentials[j].credentialType==c[i][1]) {
					result += '\
			<tr>\
				<td id="Credential-Item-'+j+'_identifier">'+data.credentials[j].identifier+'</td>\
				<td>\
					<a onclick="javascript:pageScript.RemoveCredential(\'Credential-Item-'+j+'\').doRemove(\'password\')" class="btn fa fa-trash"></a>\
				</td>\
			</tr>'
				}
			}
		}
		result +='\
		</table>'
		return result;		
	}
	
	PageScript.prototype.parseUserdata = function(data) {
		var result ='\
		<table>\
			<tr>\
				<td><b>felhasználó azonosító:</b></td>\
				<td>'+data.userid+'</td>\
			</tr>\
		</table>\
		<h4><b>Tanusítványaim:</b></h4>\
		<table>\
			<thead>\
				<tr>\
					<th>Igazolvány</th>\
					<th>Kiállító</th>\
					<th>Kiállítás dátuma</th>\
				</tr>\
			<tbody>'
		for(assurance in data.assurances) {
			console.log(data.assurances[assurance])
			for( var i=0; i<data.assurances[assurance].length; i++){
				console.log(data.assurances[assurance][i])
				result += '\
				<tr>\
					<td>'+data.assurances[assurance][i].name+'</td>\
					<td>'+data.assurances[assurance][i].assurer+'</td>\
					<td>'+self.timestampToString(data.assurances[assurance][i].timestamp)+'</td>\
				</tr>'
			}
		}
		result += '\
			</tbody>\
		</table>'
		return result
	}
		PageScript.prototype.timestampToString=function(timestamp){
			var date=new Date(timestamp*1000)
			return date.toLocaleDateString();
		}
		
	PageScript.prototype.parseAssurancing = function(data) {
		var userdata = '\
		<table>\
			<tr>\
				<td><b>e-mail cím:</b></td>\
				<td id="email-change">'+data.email+'</td>\
				<td><a onclick="javascript:pageScript.myAccountItem(\"email-change\").edit" class="btn fa fa-edit"></a></td>\
			</tr>\
			<tr>\
				<td><b>felhasználó azonosító:</b></td>\
				<td>'+data.userid+'</td>\
				<td><a onclick="javascript:pageScript.myAccountItem(\"email-change\").edit" class="btn fa fa-edit"></a></td>\
			</tr>\
			'
		userdata +='<p><b>hash:</b></p><pre>'+data.hash+"</pre>"
		userdata +="<p><b>tanusítványok:</b></p>"
		userdata +="</table><ul>"
		for(ass in data.assurances) userdata += "<li>"+ass+"</li>"; 
		userdata +="</ul>"
		userdata +="<p><b>hitelesítési módok:</b></p>"
		userdata +="<ul>"
		for(i in data.credentials) userdata += "<li>"+data.credentials[i].credentialType+"</li>" ;
		userdata +="</ul>"
		return userdata;		
	}
	
	PageScript.prototype.loginCallback=function(status, text){
		var data = JSON.parse(text)
		if (status == 200 ) {
			self.isLoggedIn=true
			self.get_me()
			self.refreshTheNavbar()
			self.displayTheSection()
		}
		else {
			this.msg = self.processErrors(data)
			this.msg.callback = self.get_me;
			self.displayMsg(this.msg);			
		}
	}
	
// oldie	
	PageScript.prototype.myCallback = function(status, text) {

		if (status!=500) {
		var data = JSON.parse(text);
	
		if (status == 200 ) {
			if( self.page=="account" && self.QueryString.next) {
				self.doRedirect(decodeURIComponent(self.QueryString.next))
			}
		}
			this.msg = self.processErrors(data)
			this.msg.callback = self.get_me;
			self.displayMsg(this.msg);
		}
		else console.log(text);
	}

	PageScript.prototype.doRedirect = function(href){ 
		win.location=href	
	}
	
	PageScript.prototype.get_me = function() {
		self.ajaxget("/v1/users/me", self.initCallback)
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		var data = JSON.parse(text);
		if (status != 200) {
//			self.menuHandler("login").menuActivate();
//			self.menuHandler("account").menuHide();
//			self.menuHandler("assurer").menuHide();
//			self.menuHandler("registration").menuUnhide();
			if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
		}
		else {
			self.isLoggedIn=true
			console.log(data)
//			if (!self.activeButton)	self.menuHandler("account").menuActivate();
//			else {
//				var a=["login", "register"];
//				if ( a.indexOf(self.activeButtonName) > -1 ) self.menuHandler("account").menuActivate();
//			}
//			self.menuHandler("login").menuHide();
//			self.menuHandler("registration").menuHide();
			if (data.assurances) {
				document.getElementById("me_Data").innerHTML=self.parseUserdata(data);
				document.getElementById("me_Settings").innerHTML=self.parseSettings(data);
//				document.getElementById("me_Applications").innerHTML=self.parseSettings(data);
//				if (data.assurances.emailverification) document.getElementById("InitiateResendRegistrationEmail_Container").style.display = 'none';
//				if (data.email) {
//					document.getElementById("AddSslCredentialForm_email_input").value=data.email;
//					document.getElementById("PasswordResetInitiateForm_email_input").value=data.email;
//				}
				console.log(data)
//				if (!(data.assurances.assurer)) self.menuHandler("assurer").menuHide();
//				else self.menuHandler("assurer").menuUnhide();
				if (!(data.assurances.assurer)) self.isAssurer=false;
				else {
					self.isAssurer=true;
					document.getElementById("assurance-giving").innerHTML=self.parseAssurancing(data);
				}
			}
//			self.fill_RemoveCredentialContainer(data);
		}
		self.refreshTheNavbar()
		if (self.page=="account") {
			if (self.QueryString.section) {
				if (self.QueryString.section!="all") self.displayTheSection(self.QueryString.section);
				else return;
			}
			else self.displayTheSection();
		}
	}

// Button actions

	PageScript.prototype.doPasswordReset = function() {
		secret = document.getElementById("PasswordResetForm_secret_input").value;
	    password = document.getElementById("PasswordResetForm_password_input").value;
	    this.ajaxpost("/v1/password_reset", {secret: secret, password: password}, this.myCallback)
	}
	
	PageScript.prototype.InitiatePasswordReset = function(myForm) {
		var emailInput=document.getElementById(myForm+"_email_input").value
		if (emailInput!="")
			self.ajaxget("/v1/users/"+document.getElementById(myForm+"_email_input").value+"/passwordreset", self.myCallback);
		else {
			emailInput.className="missing";
			this.displayMsg({"title":"Hiba","error":"Nem adtál meg email címet"})
		}
	}
	
	PageScript.prototype.login = function() {
	    username = document.getElementById("LoginForm_email_input").value;
	    var onerror=false;
		var errorMsg="";
		if (username=="") {
			errorMsg+="<p class='warning'>A felhasználónév nincs megadva</p>";
			onerror=true;
		}
	    password = document.getElementById("LoginForm_password_input").value;
	    if (password=="") {
			errorMsg+="<p class='warning'>A jelszó nincs megadva</p>";
			onerror=true; 
		}
		if (onerror==true) self.displayMsg({error:errorMsg, title:'Hibaüzenet'});
		else {
			username = encodeURIComponent(username);	
			password = encodeURIComponent(password);
			this.ajaxpost("/v1/login", {credentialType: "password", identifier: username, secret: password}, this.loginCallback)
//			document.getElementById("DeRegisterForm_identifier_input").value=username;
//			document.getElementById("DeRegisterForm_secret_input").value=password;
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
	    this.ajaxpost("/v1/login", data , this.loginCallback)
//		document.getElementById("DeRegisterForm_identifier_input").value=username;
//		document.getElementById("DeRegisterForm_secret_input").value=password;
	}

	PageScript.prototype.byEmail = function() {
	    var email = document.getElementById("ByEmailForm_email_input").value;
	    email = encodeURIComponent(email)
	    this.ajaxget("/v1/user_by_email/"+email, this.myCallback)
	}

	PageScript.prototype.logoutCallback = function(status, text) {
console.log("logoutCallback")
		data=JSON.parse(text)
		if (data.error)	self.displayError();
		else {
			var loc = '' +win.location
			var newloc = loc.replace(self.QueryString.uris.SSL_LOGIN_BASE_URL, self.QueryString.uris.BASE_URL)
			if (newloc!=loc) self.doRedirect( newloc );
			self.isLoggedIn=false
			self.refreshTheNavbar();
			if (self.page=="account") {
				self.displayTheSection("login");
			}
		}
	}
	
	PageScript.prototype.doLoadHome = function() {
		self.doRedirect(self.QueryString.uris.START_URL);
	}
	
	PageScript.prototype.logout = function() {
				console.log("logout")
	    this.ajaxget("/v1/logout", this.logoutCallback)
	}

	PageScript.prototype.sslLogin = function() {
		var loc = '' +win.location
		var newloc = loc.replace(self.QueryString.uris.BASE_URL, self.QueryString.uris.SSL_LOGIN_BASE_URL)
		self.doRedirect( newloc );
	}

	PageScript.prototype.register = function() {
		//document.getElementById('registration-keygenform').submit();
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
	    var ca = win.document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0) {
				return c.substring(name.length,c.length);
			}
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
	
	PageScript.prototype.InitiateResendRegistrationEmail = function() {
		self.displayMsg({error:'<p class="warning">Ez a funkció sajnos még nem működik</p>'});	
		}
	
	PageScript.createXmlForAnchor = function(formName) {
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
	PageScript.prototype.digestGetter = function(formName) {
		self.formName = formName
		
		self.idCallback = function(status,text,xml) {
			if (status==200) {
		    	document.getElementById(self.formName + "_digest_input").value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
				document.getElementById(self.formName + "_predigest_input").value = "";
				self.displayMsg({success:"<p class='success'>A titkosítás sikeres</p>"});
			} else {
				self.displayMsg({error:"<p class='warning'>" + text + "</p>"});
			}
		}
	
		self.getDigest = function() {
			text = PageScript.createXmlForAnchor(self.formName)
			if (text == null)
				return;
			http = this.ajaxBase(this.idCallback);
			http.open("POST",self.QueryString.uris.ANCHOR_URL+"/anchor",true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
		return self
	}

	PageScript.prototype.changeHash = function() {
	    digest = document.getElementById("ChangeHashForm_digest_input").value;
	    csrf_token = this.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/users/me/update_hash", text, this.hashCallback)
	}	
	
	PageScript.prototype.hashCallback = function(status,text) {
		if (status==200) { 
			self.displayMsg({success: "<p class='success'>A titkos kód frissítése sikeresen megtörtént</p>",
							callback: self.refreshMe });
		}
		else {
			var data = JSON.parse(text);
			self.displayMsg(self.processErrors(data));	
		}
	}
	
	PageScript.prototype.refreshMe = function() {
		self.ajaxget( '/v1/users/me', self.refreshCallback );
	} 
	
	PageScript.prototype.refreshCallback = function (status, text) {
		var data = JSON.parse(text);
		if (status==200) document.getElementById("me_Msg").innerHTML=self.parseUserdata(data);	
		else self.displayMsg(self.processErrors(data));
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
		if (email=="") self.displayMsg({error:"<p class='warning'>Nincs megadva érvényes e-mail cím</p>"});
		else self.displayMsg({error:"<p class='warning'>Ez a funkció sajnos még nem elérhető</p>"});
	}
	
	PageScript.prototype.fill_RemoveCredentialContainer = function(data) {
		var container = '';
		var i=0;
		for(CR in data.credentials) {
			container += '<div id="RemoveCredential_'+i+'">';
			container += '<table class="content_"><tr><td width="25%"><p id="RemoveCredential_'+i+'_credentialType">';
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
		container += "";
		document.getElementById("Remove_Credential_Container").innerHTML=container;
	}
	
	PageScript.prototype.RemoveCredential = function(formName) {
		self.formName = formName
		self.doRemove = function(type) {
			credentialType = (type)?type:document.getElementById(this.formName+"_credentialType").innerHTML;
			identifier = document.getElementById(this.formName+"_identifier").innerHTML;
			text = {
				csrf_token: self.getCookie("csrf"),
				credentialType: credentialType,
				identifier: identifier
			}
			this.ajaxpost("/v1/remove_credential", text, self.myCallback);
		}
		return self
	}
	
	PageScript.prototype.GoogleLogin = function(){
		self.displayMsg({error:"<p class='warning'>A google bejelentkezés funkció sajnos még nem működik</p>"});
	}
	
	PageScript.prototype.GoogleRegister = function(){
		self.displayMsg({error:"<p class='warning'>A google bejelentkezés funkció sajnos még nem működik</p>"});
	}
	
	PageScript.prototype.TwitterLogin = function(){
		self.displayMsg({error:"<p class='warning'>A twitter bejelentkezés funkció sajnos még nem működik</p>"});
	}
	
	PageScript.prototype.addPassowrdCredential = function(){
		var identifier=document.getElementById("AddPasswordCredentialForm_username_input").value;
		var secret=document.getElementById("AddPasswordCredentialForm_password_input").value;
		self.addCredential("password", identifier, secret);
	}
	
	PageScript.prototype.add_facebook_credential = function( FbUserId, FbAccessToken) {
		self.addCredential("facebook", FbUserId, FbAccessToken);
	}
	
	PageScript.prototype.addGoogleCredential = function(){
		self.displayMsg({error:"<p class='warning'>Ez a funkció sajnos még nem működik</p>"});
	}
	
	PageScript.prototype.addCredential = function(credentialType, identifier, secret) {
		var data = {
			credentialType: credentialType,
			identifier: identifier,
			secret: secret
		}
		self.ajaxpost("/v1/add_credential", data, self.addCredentialCallback)
	}

	PageScript.prototype.addCredentialCallback = function(status,text){
		var data = JSON.parse(text);
		if (status != 200) self.displayMsg({error:"<p class='warning'>"+data.errors+"</p>",title:"Hibaüzenet:"});
		else self.displayMsg({success:"<p class='success'>Hitelesítési mód sikeresen hozzáadva</p>", title:"", callback:self.get_me});
	}

	PageScript.prototype.deRegister = function() {
		self.ajaxget( "/v1/users/me", self.doDeregister )
	}
	
	PageScript.prototype.initiateDeregister = function(theForm) {
		text = { csrf_token: self.getCookie("csrf") }
		self.ajaxpost("/v1/users/deregister", text, self.myCallback)
	}
	
	PageScript.prototype.doDeregister = function(status, text) {
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
			self.ajaxpost("/v1/deregister", text, function(status, text){
				var data = JSON.parse(text);
				var msg=self.processErrors(data)
				msg.callback=self.get_me;
				self.displayMsg(msg);
			})
		}
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

		self.menuHide = function() {
			self.menuButton.style.display="none";
		}
		
		self.menuUnhide = function() {
			self.menuButton.style.display="block";
		}
		return self;
	}



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
	
	PageScript.convert_mothername = function(formName) {
		var inputElement = document.getElementById( formName+"_predigest_mothername");
		var outputElement = document.getElementById( formName+"_predigest_label_mothername_normalized");
		outputElement.innerHTML=self.normalizeString(inputElement.value);
	}
	
	PageScript.prototype.display = function(toHide, toDisplay){
		if (toHide) document.getElementById(toHide).style.display="none";
		if (toDisplay) { 
			document.getElementById(toDisplay).style.display="block";
			}
		else {
			if (self.isLoggedIn) document.getElementById("my_account_section").style.display="block";
			else document.getElementById("login_section").style.display="block";
		}
	}
	
	PageScript.prototype.queryString=function(){
		this.secret=(self.QueryString.secret)?self.QueryString.secret:"";
		this.section=(self.QueryString.section)?self.QueryString.section:"";
	}
	PageScript.prototype.getStatistics=function(){
		this.ajaxget("/v1/statistics", self.statCallback)
	}
	
	PageScript.prototype.statCallback=function(status, text) {
		data=JSON.parse(text)
		if (data.error)	self.displayError();
		else {
				document.getElementById("user-counter").innerHTML=data.users
				document.getElementById("magyar-counter").innerHTML=data.assurances.teszt
				document.getElementById("assurer-counter").innerHTML=data.assurances.assurer
				document.getElementById("application-counter").innerHTML=data.applications
			
		}
	}
	
	PageScript.prototype.refreshTheNavbar=function(){
		if (self.isLoggedIn) {
			document.getElementById("nav-bar-login").style.display="none";
			document.getElementById("nav-bar-register").style.display="none";
			document.getElementById("nav-bar-my_account").style.display="block";
			document.getElementById("nav-bar-logout").style.display="block";
		}
		else {
			document.getElementById("nav-bar-my_account").style.display="none";
			document.getElementById("nav-bar-logout").style.display="none";
			document.getElementById("nav-bar-login").style.display="block";
			document.getElementById("nav-bar-register").style.display="block";
		}
	}
}

pageScript = new PageScript();

