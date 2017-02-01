import { _ } from './gettext'
import Ajax from './ajax.js'
import { setup_the_navbar_buttons_onclick } from './setup_buttons'

window.traces = new Array();

function PageScript(test) {
	var self = this
	test=test || { debug: false, uribase: "" }
	self.debug=test.debug
	var win = test.win || window;
    self.uribase=test.uribase;
	self.isLoggedIn=false;
	self.isAssurer=false;
	self.registrationMethode="pw";
	self.isFBsdkLoaded=false;
	self.isFBconnected=false;
	self.ajax=Ajax({})
	
	PageScript.prototype.displayTheSection=function(section) {
		self.hideAllSection();
		var lis=document.getElementsByClassName("navbar-nav")[0].getElementsByTagName("li");
		[].forEach.call( lis, function (e) { e.className=""; } );
		console.log(section)
		if (!section){
			if (self.isLoggedIn){
				self.unhideSection("my_account_section")
				document.getElementById("nav-bar-my_account").className="active"
				console.log(self.isAssurer)
				if (self.isAssurer) self.unhideSection("assurer_section")
			}
			else {
				self.unhideSection("login_section")
				document.getElementById("nav-bar-login").className="active"
			}
		}
		else { 
			if (self.isLoggedIn && (section=="registration")) {
				self.unhideSection("my_account_section")
			}
			else {
				self.unhideSection(section+"_section")
				if (self.isAssurer && section=='my_account') self.unhideSection("assurer_section")
			}
			var navbar=document.getElementById("nav-bar-"+section)
			if (navbar) navbar.className="active";
		}
	}
	PageScript.prototype.hideAllSection=function(){
		[].forEach.call( document.getElementsByClassName("func"), function (e) { e.style.display="none"; } );
	}
	
	PageScript.prototype.unhideSection=function(section) {
		document.getElementById(section).style.display="block";
	}

PageScript.prototype.QueryStringFunc = function (search) { //http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-url-parameter
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

PageScript.prototype.QueryString = self.QueryStringFunc(win.location.search);
	
	PageScript.prototype.getThis=function() {
		return self
	}
	
	PageScript.prototype.reportServerFailure = function(text){
		self.displayMsg({title:_("Server error occured"),error: text})
	}
	
	PageScript.prototype.callback = self.ajax.callback
	
	PageScript.prototype.commonInit=function( response ) {
		// initialising variables
		if (self.page!='login') setup_the_navbar_buttons_onclick(self);
		var temp = self.validateServerMessage( response )
		if ( typeof temp.errors == "undefined" ) self.QueryString.uris = temp;
		else {
			self.displayMsg( self.processErrors( temp ))
			window.traces.push( 'adauris failed' )
			return
		}
		self.ajax.uribase = self.QueryString.uris.BACKEND_PATH;
		if ( typeof facebook != "undefined" && self.QueryString.uris.FACEBOOK_APP_ID ) facebook.fbinit();

		// filling hrefs of anchors
		[].forEach.call(document.getElementsByClassName("digest_self_made_button"), function(a){a.href=self.QueryString.uris.ANCHOR_URL})
		self.initialise()
		window.traces.push('initialized')
	}
	
	PageScript.prototype.ajaxBase = self.ajax.ajaxBase

	PageScript.prototype.ajaxpost = self.ajax.ajaxpost

	PageScript.prototype.ajaxget = self.ajax.ajaxget
		
	PageScript.prototype.displayServerResponse = function( response, callbacks ){
		self.displayMsg( self.processErrors( self.validateServerMessage( response ), callbacks ) )
	}
	
	PageScript.prototype.validateServerMessage = self.ajax.validateServerMessage
	
	PageScript.prototype.processErrors = function(data, callbacks) {
		console.log(data)
			var msg = {}, 
				translateError = function(e){
					console.log(e)
					var a=e.split(': ');
					for(var i=0; i<a.length; i++){
						a[i]=_(a[i])
					}
					return a.join(': ')
				};
			if (callbacks) msg.callback = callbacks.ok || null;
			if (data.message) {
				msg.title=_("Server message");
				msg.message=self.parseMessage(data.message)
				if (typeof msg.message=="string") {
                    msg.message="<p>"+msg.message+"</p>";
				} else {
                    var a="<ul>"
		            for( var value in msg.message) {
                        a += "<li>"+msg.message[value]+"</li>";
                    }
                    a+="</ul>";
                    msg.message=a;
                }
                console.log("message out: %o", msg.message)
			}
			
			if (data.assurances) {
				msg.title=_("User informations");
				msg.success=self.parseUserdata(data);
			}
			
			if (data.errors) {
				msg.title = _("Error message")
				msg.error = '<ul class="disced">';
				var errs = data.errors;
				if (typeof(errs)!='string') {
					[].forEach.call(errs, function(e) {
						msg.error += "<li>"+ translateError(e) +"</li>" ;})
				}
				else {
					msg.error += "<li>"+ translateError(errs) +"</li>";
				}
				msg.error += "</ul>";
			}
			console.log(msg)
			return msg;
	}
	
	PageScript.prototype.parseMessage = function(value,key,arr)  {
		if (typeof value == "string"){
			if (key==undefined || key!=0) return _(value)
			var pars=arr;
			pars.shift();
			return _(value, pars.map(function(v,k){return _(v)}))
		}
		if (typeof value[0]=="string") return self.parseMessage(value[0],0,value)
		var a=[];
		value.forEach( function(v,k,arr){a.push(self.parseMessage(v))})
		return a
	}
	
	PageScript.prototype.setAppCanEmailMe=function(appId, value, callback){
		if (self.aps && self.aps[appId]) {
			var	data= {
				canemail: value,
				appname: self.aps[appId].name,
				csrf_token: self.getCookie('csrf')
				}
			self.ajaxpost("/v1/setappcanemail", data, self.callback(callback))
		}
		else self.displayMsg({title:_("Error message"),error:_("The application does not exist.")})
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
		for( var assurance in data.assurances) {
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
	
// oldie	
	PageScript.prototype.myCallback = function(response) {
		if( self.page=="login"){
			if( self.QueryString.next) {
				self.doRedirect(decodeURIComponent(self.QueryString.next))
			}
		}
		self.displayServerResponse(response);
	}
	
	PageScript.prototype.meCallback = function(response) {
		self.get_me()
		self.displayServerResponse(response)
	}

	PageScript.prototype.registerCallback = function(text) {
		self.isLoggedIn=true
		if( self.page=="account"){
			var msg={
				title:_("Congratulation!"),
				error:_("You have succesfully registered and logged in. </br> Please click the link inside the email we sent you to validate your email address, otherwise your account will be destroyed in one week.")
				}
			self.displayMsg(msg)
			self.userIsLoggedIn (text)
		}
		if( self.page=="login"){
			self.ajaxget('/v1/getmyapps',self.callback(self.finishRegistration))
		}
		window.traces.push("registerCallback")
	}	

	PageScript.prototype.reloadCallback = function(response) {
		self.displayServerResponse(response, {ok:self.doLoadHome})
	}
	
	PageScript.prototype.doRedirect = function(href){ 
		win.location=href	
	}
	
	PageScript.prototype.doLoadHome = function() {
		self.doRedirect(self.QueryString.uris.START_URL);
	}
	
	PageScript.prototype.get_me = function() {
		self.ajaxget("/v1/users/me", self.callback(self.userIsLoggedIn, self.userNotLoggedIn))
	}
	
// Button actions

	PageScript.prototype.doPasswordReset = function() {
		var secret = document.getElementById("PasswordResetForm_secret_input").value,
			password = document.getElementById("PasswordResetForm_password_input").value;
	    this.ajaxpost("/v1/password_reset", {secret: secret, password: password}, self.callback(self.reloadCallback))
	}
	
	PageScript.prototype.InitiatePasswordReset = function(myForm) {
		var emailInput=document.getElementById(myForm+"_email_input")
		if (emailInput!="")
			self.ajaxget("/v1/users/"+self.mailRepair(emailInput.value)+"/passwordreset", self.callback(self.myCallback));
		else {
			emailInput.className="missing";
			this.displayMsg({"title":"Hiba","error":"Nem adtál meg email címet"})
		}
	}
	
    PageScript.prototype.mailRepair = function(mail) {
        return self.mail = mail.replace(/\s+/g,'').toLowerCase();
	}
	
	PageScript.prototype.justLoggedIn = function(response){
		self.QueryString.section='my_account'
		self.userIsLoggedIn(response)
	}
	
	PageScript.prototype.login = function() {
	    var username = document.getElementById("LoginForm_email_input").value,
			onerror=false,
			errorMsg="",
			password = document.getElementById("LoginForm_password_input").value;
		if (username=="") {
			errorMsg+=_("User name is missing. ");
			onerror=true;
		}
	    if (password=="") {
			errorMsg+=_("Password is missing. ");
			onerror=true; 
		}
		if (onerror==true) self.displayMsg({error:errorMsg, title:_("Missing data")});
		else {
			var data = {
				credentialType: "password", 
				identifier: username, 
				password: password
				}
			self.ajaxpost( "/v1/login", data, self.callback(self.justLoggedIn) )
		}
	}

	PageScript.prototype.login_with_facebook = function(userId, accessToken) {
		console.log("facebook login")
	    var data = {
				credentialType: 'facebook',
				identifier: userId,
				password: encodeURIComponent(accessToken)
			}
	    self.ajaxpost("/v1/login", data , self.callback(self.justLoggedIn) )
	}
	
	PageScript.prototype.logout = function() {
		console.log(self.QueryString)
	    self.ajaxget("/v1/logout", self.callback( function(){self.doRedirect( self.QueryString.uris.START_URL)} ))
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

	PageScript.prototype.RemoveCredential = function(formName) {
		self.formName = formName
		this.doRemove = function(type) {
			var credentialType = (type)?type:document.getElementById(this.formName+"_credentialType").innerHTML,
				identifier = document.getElementById(this.formName+"_identifier").innerHTML,
				text = {
					csrf_token: self.getCookie("csrf"),
					credentialType: credentialType,
					identifier: identifier
				}
			console.log("text")
			this.ajaxpost("/v1/remove_credential", text, self.callback(self.meCallback));
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

//Getdigest functions	
	PageScript.prototype.normalizeString = function(val) {
		var   accented="öüóőúéáűíÖÜÓŐÚÉÁŰÍ",
			unaccented="ouooueauiouooueaui",
			s = "",
			c;
		
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
	
	// removing all non numeric characters
	PageScript.prototype.normalizeId = function(val) {
		return val.replace(/[^0-9]/g,"");
	}
	
	PageScript.prototype.digestGetter = function(formName) {
		var formName=formName,
		digestCallback = function(status,text,xml) {
			var diegestInput=document.getElementById(formName + "_digest_input")
			if (status==200) {
				window.traces.push("digest cb")
				diegestInput.value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
				console.log(diegestInput.value)
				$("#"+formName + "_digest-input").trigger('keyup');
				document.getElementById(formName + "_predigest_input").value = "";
				switch (formName) {
					case "assurancing":
						var messageBox=document.getElementById("assurance-giving_message")
						messageBox.innerHTML=_("The Secret Hash is given for assuring")
						messageBox.className="given"
						document.getElementById("assurance-giving_submit-button").className=""
						break;
					case "login":
					case "change-hash-form":
						self.changeHash()
						break;
					case "registration-form":
						console.log("formname is " + formName)
						var style = document.getElementById(formName+"_code-generation-input").style;
						console.log("style:" + formName)
						style.display="none"
						document.getElementById(formName+"_digest_input").style.display="block"
						self.activateButton( formName+"_make-here", function(){self.digestGetter(formName).methodChooser('here')})
						break;
					default:
						style.display="none"
				}
				window.traces.push("gotDigest")
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
			var text = createXmlForAnchor(formName)
			if (text == null) return;
			var http = self.ajaxBase(digestCallback);
			http.open("POST",self.QueryString.uris.ANCHOR_URL+"anchor",true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
	
		function createXmlForAnchor(formName) {
			console.log(formName)
			var personalId = self.normalizeId(document.getElementById(formName+"_predigest_input").value),
				motherValue = document.getElementById(formName+"_predigest_mothername").value,
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
		outputElement.innerHTML = self.normalizeId(document.getElementById( formName+"_input").value) +' - '+ self.normalizeString(inputElement.value);
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
				document.getElementById("registration-form_secret_input").value="";
				document.getElementById("registration-form_identifier_input").value="";
			break;
			case "fb":
				heading=_("my facebook account")
				document.getElementById("registration-form-password-container").style.display="none";
				document.getElementById("registration-form-username-container").style.display="none";
				facebook.fbregister()
			break;
		}
		document.getElementById("registration-form-method-heading").innerHTML=_("Registration with %s ",heading);
	}

	PageScript.prototype.register = function(credentialType) {
		//
	    var identifier = (document.getElementById("registration-form_identifier_input").value=="")?
			document.getElementById("registration-form_email_input").value:
			document.getElementById("registration-form_identifier_input").value,
			secret = document.getElementById("registration-form_secret_input").value,
			email = self.mailRepair(document.getElementById("registration-form_email_input").value),
			d=document.getElementById("registration-form_digest_input"),
			digest =(d)?d.value:"",
			data= {
	    	credentialType: credentialType,
	    	identifier: identifier,
	    	email: email,
	    	digest: digest,
			password: secret
	    }
		window.traces.push(data)
		window.traces.push("register")
	    self.ajaxpost("/v1/register", data, self.callback(self.registerCallback))
	}

	PageScript.prototype.doRegister=function() {
		if ( document.getElementById("registration-form_confirmField").checked ) {
			console.log(self.registrationMethode)
			switch (self.registrationMethode) {
				case "pw":
					console.log('pw')
					var pwInput=document.getElementById("registration-form_secret_input")
					var pwBackup=document.getElementById("registration-form_secret_backup")
					if (pwInput.value!=pwBackup.value) self.displayMsg({title:_("Error message"),error:_("The passwords are not identical")})
					else self.register("password")
					break;
				case "fb":
					console.log('fb')
					self.register("facebook")
					break;
			}
		}
		else self.displayMsg({title:_("Acceptance is missing"),error:_("For the registration you have to accept the terms of use. To accept the terms of use please mark the checkbox!")})
	}
	
	PageScript.prototype.deactivateButton = function(buttonId) {
		var b=document.getElementById(buttonId)
		if (b) {
			b.className+=" inactive";
			b.onclick=function(){return}
		}		
	}
	
	PageScript.prototype.activateButton = function(buttonId, onclickFunc) {
		var b=document.getElementById(buttonId),
			c
		if (b) {
			b.className=b.className.slice(0,b.className.indexOf("inactive"))
			b.onclick = onclickFunc 
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
	
	PageScript.prototype.setCookie = function( cname, cvalue, expireDays ) {
		var d = new Date(),	expireDays = expireDays || 1;
    	d.setTime(d.getTime() + (expireDays*24*60*60*1000));
    	var expires = "expires="+ d.toUTCString();
    	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
	} 

	self.ajax.displayServerResponse= self.displayServerResponse
	self.ajax.reportServerFailure= self.reportServerFailure
}

export {facebook}
export default PageScript
