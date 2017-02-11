import { _ } from './gettext'
import * as Ajax from './ajax.js'
import { setup_the_navbar_buttons_onclick } from './setup_buttons'
import { uris } from './adauris'
import * as Cookie from './cookie'
import * as Control from './control'
import * as Msg from './messaging'

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
	
	PageScript.prototype.displayTheSection=function(section) {
		self.hideAllSection();
		var lis=document.getElementsByClassName("navbar-nav")[0].getElementsByTagName("li");
		[].forEach.call( lis, function (e) { e.className=""; } );
		console.log(section)
		if (!section){
			if (self.isLoggedIn){
				console.log("display the section is logged in")
				Control.show("my_account_section")
				document.getElementById("nav-bar-my_account").className="active"
				console.log(self.isAssurer)
				if (self.isAssurer) Control.show("assurer_section")
			}
			else {
				Control.show("login_section")
				document.getElementById("nav-bar-login").className="active"
			}
		}
		else { 
			if (self.isLoggedIn && (section=="registration")) {
				Control.show("my_account_section")
			}
			else {
				Control.show(section+"_section")
				if (self.isAssurer && section=='my_account') Control.show("assurer_section")
			}
			var navbar=document.getElementById("nav-bar-"+section)
			if (navbar) navbar.className="active";
		}
	}
	PageScript.prototype.hideAllSection=function(){
		[].forEach.call( document.getElementsByClassName("func"), function (e) { e.style.display="none"; } );
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
		Msg.display({title:_("Server error occured"),error: text})
	}
	
	PageScript.prototype.callback = Ajax.callback
	
	PageScript.prototype.commonInit=function() {
		// initialising variables
		if (self.page!='login') setup_the_navbar_buttons_onclick(self);
		self.QueryString.uris = uris;
		if ( typeof facebook != "undefined" && self.QueryString.uris.FACEBOOK_APP_ID ) facebook.fbinit();

		// filling hrefs of anchors
		[].forEach.call(document.getElementsByClassName("digest_self_made_button"), function(a){a.href=self.QueryString.uris.ANCHOR_URL})
		self.initialise()
		window.traces.push('initialized')
	}
	
	PageScript.prototype.ajaxBase = Ajax.base

	PageScript.prototype.ajaxpost = Ajax.ajaxpost

	PageScript.prototype.ajaxget = Ajax.ajaxget
		
	PageScript.prototype.displayServerResponse = function( response, callbacks ){
		Msg.display( self.processErrors( self.validateServerMessage( response ), callbacks ) )
	}
	
	PageScript.prototype.validateServerMessage = Ajax.validateServerMessage
	
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
				csrf_token: Cookie.get('csrf') || ""
				}
			self.ajaxpost("/v1/setappcanemail", data, self.callback(callback))
		}
		else Msg.display({title:_("Error message"),error:_("The application does not exist.")})
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
			Msg.display(msg)
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
		if (onerror==true) Msg.display({error:errorMsg, title:_("Missing data")});
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
	


	PageScript.prototype.RemoveCredential = function(formName) {
		self.formName = formName
		this.doRemove = function(type) {
			var credentialType = (type)?type:document.getElementById(this.formName+"_credentialType").innerHTML,
				identifier = document.getElementById(this.formName+"_identifier").innerHTML,
				text = {
					csrf_token: Cookie.get("csrf") || "",
					credentialType: credentialType,
					identifier: identifier
				}
			console.log("text")
			this.ajaxpost("/v1/remove_credential", text, self.callback(self.meCallback));
		}
		return self
	}
	
	PageScript.prototype.GoogleLogin = function(){
		Msg.display({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.GoogleRegister = function(){
		Msg.display({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.TwitterLogin = function(){
		Msg.display({title:_("Under construction"), error:_("This function is not working yet.")});	
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
					if (pwInput.value!=pwBackup.value) Msg.display({title:_("Error message"),error:_("The passwords are not identical")})
					else self.register("password")
					break;
				case "fb":
					console.log('fb')
					self.register("facebook")
					break;
			}
		}
		else Msg.display({title:_("Acceptance is missing"),error:_("For the registration you have to accept the terms of use. To accept the terms of use please mark the checkbox!")})
	}


	Ajax.set_displayServerResponse( self.displayServerResponse )
	Ajax.set_reportServerFailure( self.reportServerFailure )
}

export {facebook}
export default PageScript
