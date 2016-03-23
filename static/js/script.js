function PageScript(test) {
	var self = this
	test=test || { debug: false, uribase: "" }
	this.debug=test.debug
	win = test.win || window;
    self.uribase=test.uribase;
	this.isLoggedIn=false;
	this.isAssurer=false;
	this.registrationMethode="pw";

PageScript.prototype.QueryStringFunc = function (search) { //http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-url-parameter
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  win=win || window 			// to be testable
  var query_string = {};
  var query = search.substring(1);
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

    this.QueryString = self.QueryStringFunc(win.location.search);
	
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
			var translateError =function(e){
				var a=e.split(': ');
				for(var i=0; i<a.length; i++){
					a[i]=_(a[i])
				}
				return a.join(': ')
			}
			if (data.message) {
				msg.title=_("Server message");
				msg.message="<p>"+_(data.message)+"</p>";
			}
			if (data.assurances) {
				msg.title=_("User informations");
				msg.success=self.parseUserdata(data);
			}
			if (data.errors) {
				msg.title = _("Error message")
				msg.error = '<ul class="disced">';
				errs = data.errors;
				console.log(errs)
				if (typeof(errs)!='string') {
					[].forEach.call(errs, function(e) {
						msg.error += "<li>"+ translateError(e) +"</li>" ;})
				}
				else {
					msg.error += "<li>"+ translateError(errs) +"</li>";
				}
				msg.error += "</ul>";
			}
			return msg;
	}
	
	PageScript.prototype.myappsCallback = function(status,text){
		if (status!=200) return;
		self.aps=JSON.parse(text)
		var applist='\
		<table>\
			<tr>\
				<th>'+_("Application")+'</th>\
				<th>'+_("Domain")+'</th>\
				<th>'+_("User identifier")+'</th>\
				<th>'+_("Emailing")+'</th>\
				<th>'+_("Allow emailing")+'</th>\
			</tr>'
		for(app in self.aps){ 
		if (self.aps[app].username) { 
			applist+='\
			<tr>\
				<td>'+self.aps[app].name+'</td>\
				<td><a href="//'+self.aps[app].hostname+'">'+self.aps[app].hostname+'</a></td>\
				<td>'+self.aps[app].username+'</td>\
				<td>'+_(self.aps[app].can_email.toString())+'</td>\
				<td>\
					<input type="checkbox" id="application-allow-email-me-'+app+'"\
					'+((self.aps[app].email_enabled)?'checked':'')+'\
					onclick="javascript: pageScript.setAppCanEmailMe('+app+')">\
				</td>\
			</tr>'
			}	
		}
		applist +='\
		</table>';
		document.getElementById("me_Applications").innerHTML=applist;
	}
	
	PageScript.prototype.setAppCanEmailMe=function(app){
		var value=document.getElementById("application-allow-email-me-"+app).checked
		var csrf_token = self.getCookie('csrf');
	    text= {
			canemail: value,
	    	appname: self.aps[app].name,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/setappcanemail", text, this.myCallback)
	}
	
	PageScript.prototype.parseUserdata = function(data) {
		var result ='\
		<table>\
			<tr>\
				<td><b>'+_("User identifier")+'</b></td>\
				<td>'+data.userid+'</td>\
			</tr>\
		</table>\
		<h4><b>'+_("Assurances")+'</b></h4>\
		<table>\
			<thead>\
				<tr>\
					<th>'+_("Name")+'</th>\
					<th>'+_("Assurer")+'</th>\
					<th>'+_("Date of assurance")+'</th>\
					<th>'+_("Valid until")+'</th>\
				</tr>\
			<tbody>'
		for(assurance in data.assurances) {
			for( var i=0; i<data.assurances[assurance].length; i++){
				result += '\
				<tr>\
					<td>'+_(data.assurances[assurance][i].name)+'</td>\
					<td>'+data.assurances[assurance][i].assurer+'</td>\
					<td>'+self.timestampToString(data.assurances[assurance][i].timestamp)+'</td>\
					<td>'+
//					self.timestampToString(data.assurances[assurance][i].valid)+
					_("unlimited")+
					'</td>\
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
		
	PageScript.prototype.parseAssurances = function(data) {
		var selector = ''
		var text
		for(ass in data.assurances) {
			var pos
			if ( pos=ass.indexOf(".")+1 ) {
				text=ass.slice(pos)
				selector += '\
				<option value="'+text+'">\
				'+_(text)+'\
				</option>\
				';
			}
		}
		return selector;		
	}
	
	PageScript.prototype.loginCallback=function(status, text){
		var data = JSON.parse(text)
		if (status == 200 ) {
			self.isLoggedIn=true
			self.get_me()
			document.getElementById("LoginForm_password_input").value=""
			document.getElementById("LoginForm_email_input").value=""
		}
		else {
			this.msg = self.processErrors(data)
			self.displayMsg(this.msg);			
		}
	}
	
// oldie	
	PageScript.prototype.myCallback = function(status, text) {

		if (status!=500) {
			var data = JSON.parse(text);
			var msg = self.processErrors(data)
			if (status == 200 ) {
				if( self.page=="login"){
					if( self.QueryString.next) {
						self.doRedirect(decodeURIComponent(self.QueryString.next))
					}
				}
			}
			self.displayMsg(msg);
		}
		else console.log(text);
	}
	
	PageScript.prototype.meCallback = function(status, text) {
		if (status!=500) {
			var data = JSON.parse(text);
			var msg = self.processErrors(data)
			if (status == 200 ) {
				if( self.page=="account"){
					self.get_me()
				}
				if( self.page=="login"){
					self.init_();
				}
			}
			else self.displayMsg(msg);
		}
		else console.log(text);
	}
	PageScript.prototype.registerCallback = function(status, text) {
		if (status!=500) {
			var data = JSON.parse(text);
			var msg = self.processErrors(data)
			if (status == 200 ) {
				if( self.page=="account"){
					self.get_me()
				}
				if( self.page=="login"){
					self.dataGivingAccepted=true
					self.ajaxget('/v1/getmyapps',self.myappsCallback)
				}
			}
			else self.displayMsg(msg);
		}
		else console.log(text);
	}	

	PageScript.prototype.reloadCallback = function(status, text) {
		if (status!=500) {
			var data = JSON.parse(text);
			var msg = self.processErrors(data)
			if (status == 200 ) {
				if( self.page=="account"){
					if( self.QueryString.next) {
						self.doRedirect(decodeURIComponent(self.QueryString.next))
					}
					msg.callback = function(){self.doRedirect("fiokom.html")};
				}
			}
			self.displayMsg(msg);
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
		console.log("initcallback "+status)
		var data = JSON.parse(text);
		if (status != 200) {
//			self.menuHandler("login").menuActivate();
//			self.menuHandler("account").menuHide();
//			self.menuHandler("assurer").menuHide();
//			self.menuHandler("registration").menuUnhide();
			if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
		}
		else {
			self.ajaxget('/v1/getmyapps',self.myappsCallback)
			self.isLoggedIn=true
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
				document.getElementById("assurance-giving_assurance_selector").innerHTML=self.parseAssurances(data);
//				if (data.assurances.emailverification) document.getElementById("InitiateResendRegistrationEmail_Container").style.display = 'none';
//				if (data.email) {
//					document.getElementById("AddSslCredentialForm_email_input").value=data.email;
//					document.getElementById("PasswordResetInitiateForm_email_input").value=data.email;
//				}
//				if (!(data.assurances.assurer)) self.menuHandler("assurer").menuHide();
//				else self.menuHandler("assurer").menuUnhide();
				if (!(data.assurances.assurer)) self.isAssurer=false;
				else {
					self.isAssurer=true;
//					document.getElementById("assurance-giving").innerHTML=self.parseAssurancing(data);
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
	    this.ajaxpost("/v1/password_reset", {secret: secret, password: password}, this.reloadCallback)
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
			errorMsg+=_("User name is missing. ");
			onerror=true;
		}
	    password = document.getElementById("LoginForm_password_input").value;
	    if (password=="") {
			errorMsg+=_("Password is missing. ");
			onerror=true; 
		}
		if (onerror==true) self.displayMsg({error:errorMsg, title:_("Missing data")});
		else {
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


	PageScript.prototype.logoutCallback = function(status, text) {
console.log("logoutCallback")
		data=JSON.parse(text)
		if (data.error)	self.displayError();
		else {
			var loc = '' +win.location
			var newloc = loc.replace(self.QueryString.uris.SSL_LOGIN_BASE_URL, self.QueryString.uris.BASE_URL)
			if (newloc!=loc) self.doRedirect( newloc );
			else {
				self.isLoggedIn=false
				self.doRedirect( self.QueryString.uris.START_URL)
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

	PageScript.prototype.InitiateResendRegistrationEmail = function() {
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
		}
/*	
	PageScript.prototype.refreshMe = function() {
		self.ajaxget( '/v1/users/me', self.refreshCallback );
	} 
	
	PageScript.prototype.refreshCallback = function (status, text) {
		var data = JSON.parse(text);
		if (status==200) document.getElementById("me_Msg").innerHTML=self.parseUserdata(data);	
		else self.displayMsg(self.processErrors(data));
	}
*/

	PageScript.prototype.loadjs = function(src) {
	    var fileref=document.createElement('script')
	    fileref.setAttribute("type","text/javascript")
	    fileref.setAttribute("src", src)
	    document.getElementsByTagName("head")[0].appendChild(fileref)
	}
	
	PageScript.prototype.unittest = function() {
		this.loadjs("ts.js")
	}
	
	PageScript.prototype.changeEmailAddress = function() {
	    email = document.getElementById("ChangeEmailAddressForm_email_input").value;
		if (email=="") self.displayMsg({error:"<p class='warning'>Nincs megadva érvényes e-mail cím</p>"});
		else self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
//obsolote	
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
		this.doRemove = function(type) {
			credentialType = (type)?type:document.getElementById(this.formName+"_credentialType").innerHTML;
			identifier = document.getElementById(this.formName+"_identifier").innerHTML;
			text = {
				csrf_token: self.getCookie("csrf"),
				credentialType: credentialType,
				identifier: identifier
			}
			console.log("text")
			this.ajaxpost("/v1/remove_credential", text, self.meCallback);
		}
		return self
	}
	
	PageScript.prototype.GoogleLogin = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.GoogleRegister = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.TwitterLogin = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addPasswordCredential = function(){
		var identifier=document.getElementById("AddPasswordCredentialForm_username_input").value;
		var secret=document.getElementById("AddPasswordCredentialForm_password_input").value;
		self.addCredential("password", identifier, secret);
	}
	
	PageScript.prototype.add_facebook_credential = function( FbUserId, FbAccessToken) {
		self.addCredential("facebook", FbUserId, FbAccessToken);
	}
	
	PageScript.prototype.addGoogleCredential = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addGithubCredential = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addTwitterCredential = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.doDeregister = function() {
		if ( document.getElementById("accept_deregister").checked ) {
			if ( self.QueryString.secret ) {
				text = {	csrf_token: self.getCookie("csrf"),
							deregister_secret: self.QueryString.secret
							}
				self.ajaxpost( "/v1/deregister_doit", text, self.deregisterCallback )
			}
			else {
				var msg={ 	title:_("Error message"),
							error:_("The secret is missing")}
				self.displayMsg(msg);			
			}
		}
		else {
			var msg={ 	title:_("Error message"),
						error:_("To accept the terms please mark the checkbox!")}
			self.displayMsg(msg);	
		}			
	}
	
	PageScript.prototype.initiateDeregister = function(theForm) {
		text = { csrf_token: self.getCookie("csrf") }
		self.ajaxpost("/v1/deregister", text, self.myCallback)
	}
	
	PageScript.prototype.deregisterCallback = function(status, text) {
		var data = JSON.parse(text);
		var msg=self.processErrors(data)
		if (status == 200) {
			self.isLoggedIn=false
			self.refreshTheNavbar();
			if (self.page=="account") {
				self.displayTheSection("login");
			}
			msg.callback=function(){self.doRedirect(self.QueryString.uris.START_URL)};
		}
		self.displayMsg(msg);
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

	PageScript.prototype.sslLogin = function() {
		console.log("sslLogin")
		var xmlhttp = this.ajaxBase( self.initCallback )
		xmlhttp.open( "GET", self.QueryString.uris.SSL_LOGIN_BASE_URL+self.uribase+'/v1/ssl_login' , true);
		xmlhttp.send();
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
				switch (formName) {
					case "assurancing":
						var messageBox=document.getElementById("assurance-giving_message")
						messageBox.innerHTML=_("The Secret Hash is given for assuring")
						messageBox.className="given"
						document.getElementById("assurance-giving_submit-button").className=""
						break;
					case "login":
						self.changeHash()
						break;
					case "registration-form":
						document.getElementById(formName+"_code-generation-input").style.display="none"
						document.getElementById(formName+"_digest-input").style.display="block"
						self.activateButton( formName+"_make-here", function(){self.digestGetter(formName).methodChooser('here')})
						break;
					default:
						document.getElementById(formName+"_code-generation-input").style.display="none"
				}
			}
			else {
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

		this.methodChooser = function(method) {
			var selfButton = formName+"_make-self"
			var hereButton = formName+"_make-here"
			switch (method) {
				case "here":
					document.getElementById(formName+"_code-generation-input").style.display="block"
					document.getElementById(formName+"_digest-input").style.display="none"
					self.activateButton( selfButton, function(){self.digestGetter(formName).methodChooser('self')} )
					self.deactivateButton( hereButton )
					break;
				case "self":
					document.getElementById(formName+"_code-generation-input").style.display="none"
					document.getElementById(formName+"_digest-input").style.display="block"
					self.activateButton( hereButton, function(){self.digestGetter(formName).methodChooser('here')} )
					self.deactivateButton( selfButton )
					break;
				default:
			}
		}
		
		this.getDigest = function() {
			text = createXmlForAnchor(formName)
			if (text == null) return;
			http = self.ajaxBase(digestCallback);
			http.open("POST",self.QueryString.uris.ANCHOR_URL+"anchor",true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
	
		function createXmlForAnchor(formName) {
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
		document.getElementById("registration-form-method-heading").innerHTML=_("Registration with %s ",heading);
	}

	PageScript.prototype.register = function(credentialType) {
		//
	    var identifier = (document.getElementById("registration-form_identifier_input").value=="")?
			document.getElementById("registration-form_email_input").value:
			document.getElementById("registration-form_identifier_input").value;
	    var secret = document.getElementById("registration-form_secret_input").value;
	    var email = document.getElementById("registration-form_email_input").value;
		var d;
		var digest =(d=document.getElementById("registration-form_digest_input"))?d.value:"";
	    var text= {
	    	credentialType: credentialType,
	    	identifier: identifier,
	    	secret: secret,
	    	email: email,
	    	digest: digest
	    }
		console.log(text)
	    this.ajaxpost("/v1/register", text, this.registerCallback)
	}
	
	PageScript.prototype.onSslRegister= function(){
		console.log('ssl_onSslRegister')
		if (self.sslCallback()) self.sslLogin();
	}

	PageScript.prototype.addSslCredentialCallback= function(){
		if (self.sslCallback()) self.getMe();
	}

	PageScript.prototype.doRegister=function() {
		if ( document.getElementById("registration-form_confirmField").checked ) {
			console.log(self.registrationMethode)
			switch (self.registrationMethode) {
				case "pw":
					console.log('pw')
					var pwInput=document.getElementById(formName+"registration-form_secret_input")
					var pwBackup=document.getElementById(formName+"registration-form_secret_backup")
					if (pwInput.value!=pwBackup.value) self.displayMsg({title:_("Error message"),error:_("The passwords are not identical")})
					else self.register("password")
					break;
				case "fb":
					console.log('fb')
					self.register("facebook")
					break;
				case "ssl":
					console.log('ssl_register')
					document.getElementById("SSL").onload=self.onSslRegister;
					document.getElementById('registration-keygenform').submit();
					console.log("after submit")
//					self.doRedirect(self.QueryString.uris.SSL_LOGIN_BASE_URL+"fiokom.html")
					break;
			}
		}
		else self.displayMsg({title:_("Acceptance is missing"),error:_("For the registration you have to accept the terms of use. To accept the terms of use please mark the checkbox!")})
	}
	
	PageScript.prototype.sslCallback=function() {
		console.log("sslCallback")
		response=document.getElementById("SSL").contentDocument.body.innerHTML
		console.log(response)
		if (response!="")  {
			var msg
			if (data=JSON.parse(response)) {
				msg=self.processErrors(data)
			}
			else {
				msg.title=_("Server failure")
				msg.error=response
			}
			self.displayMsg(msg)
			return false
		}
		else return true
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
			b.className=b.className.slice(0,b.className.indexOf("inactive"))
			b.onclick=onclickFunc
		}
	}

	PageScript.prototype.passwordChanged = function(formName) {
		var strength = document.getElementById(formName+"_pw-strength-meter");
		var strongRegex = new RegExp("^(?=.{10,})((?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[^a-zA-Z0-9_])).*$", "g");
		var mediumRegex = new RegExp("^(?=.{8,})((?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", "g");
		var enoughRegex = new RegExp("(?=.{8,}).*", "g");
		var pwd = document.getElementById(formName+"_secret_input");
		if (pwd.value.length==0) {
			strength.innerHTML = _('Type Password');
		} 
		else if (false == enoughRegex.test(pwd.value)) {
				strength.innerHTML = _("More Characters");
			} 
			else if (strongRegex.test(pwd.value)) {
					strength.innerHTML = '<span style="color:green">'+_("Strong!")+'</span>';
				} 
				else if (mediumRegex.test(pwd.value)) {
						strength.innerHTML = '<span style="color:orange">'+_("Medium!")+'</span>';
					} 
					else {
						strength.innerHTML = '<span style="color:red">'+_("Weak!")+'</span>';	
					}
		self.pwEqual(formName)
	}
	
	PageScript.prototype.pwEqual = function(formName) {
		var pwInput=document.getElementById(formName+"_secret_input")
		var pwBackup=document.getElementById(formName+"_secret_backup")
		var pwEqual=document.getElementById(formName+"_pw-equal")
		if (pwInput.value==pwBackup.value) pwEqual.innerHTML = '<span style="color:green">'+_("OK.")+'</span>';	
		else pwEqual.innerHTML = '<span style="color:red">'+_("Passwords are not equal.")+'</span>';	
	}
}
	
pageScript = new PageScript();

/* 
==============================================
Back To Top Button
=============================================== */  
 
  $(window).scroll(function () {
            if ($(this).scrollTop() > 50) {
                $('#back-top').fadeIn();
            } else {
                $('#back-top').fadeOut();
            }
        });
      // scroll body to 0px on click
      $('#back-top').click(function () {
          $('#back-top a').tooltip('hide');
          $('body,html').animate({
              scrollTop: 0
          }, 800);
          return false;
      });
      
      if ($('#back-top').length!=0) $('#back-top').tooltip('hide');
