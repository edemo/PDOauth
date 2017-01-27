(function(){	
	var self
	PageScript.prototype.page = "account";
	PageScript.prototype.main = function() {
		self=this.getThis()
		var xxxx=self
		this.ajaxget("/adauris", self.callback(self.commonInit), true)
		var section = self.QueryString.section
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
					if (self.QueryString.secret) {
						document.getElementById("PasswordResetForm_secret_input").value=self.QueryString.secret
					}
					break;
				case "deregistration" :
					self.QueryString.section="deregistration"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "emailcheck" :
					self.QueryString.section="email_verification"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "cancelemailchange" :
					self.QueryString.section="cancelemailchange"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "emailchange" :
					self.QueryString.section="emailchange"
					self.unhideSection(self.QueryString.section+"_section")
					break;
				case "login" :
					self.unhideSection(section+"_section")
					break;
				default:
			}
		window.traces.push("main end")
	}
	
	PageScript.prototype.fillAssurersTable = function(txt, xml){
		try { 
			self.assurers=JSON.parse(txt) 
		}
		catch(err) { 
			console.log(err.message)
			return
		}
		[].forEach.call( self.assurers.assurers, function(assurer) {
			// the record will not be displayed if availability is false
			if (assurer.availability){
				var row=$('<tr></tr>')
				$(row).append( $('<td>'+assurer.name+'</td>') )
				var districts=$('<ul></ul>');
				[].forEach.call( assurer.districts, function(district) {
					$(districts).append('<li>'+district+'</li>')
				} )
				$(row).append( $('<td></td>').append( $(districts) ) )
				var assurances=$('<ul></ul>');
				[].forEach.call( assurer.assurances, function(assurance) {
					$(assurances).append('<li>'+_(assurance.assurance)+'</li>')
				} )
				$(row).append( $('<td></td>').append( $(assurances) ) )
				$(row).append( $('<td nowrap></td>').append( 
					$('<a href="mailto:'+assurer.email+'"></a>').append( 
					$('<button class="social" title="'+_("Open in your mail client")+'"></button>').append('<i class="fa fa-envelope"></i>') )
				).append(
					$('<button class="social" style="margin-left:5px" title="'+_("Copy email address to clipboard")+'"></button>'
					).click(function(){self.copyEmailAddressToClipboard(assurer.email)}).append('<i class="fa fa-clipboard"></i>')
				) )
				$("#assurers_table tbody").append(row)
			}
		} ) 
	}
	
	PageScript.prototype.copyEmailAddressToClipboard = function(text) {	
		if (!document.queryCommandSupported('copy')) alert(text)
		else { 
			var textArea = $('<textarea class="tmp_clpbrd">').append(text)
			$("body").append( textArea )
			textArea.select();
			try {
				var successful = document.execCommand('copy');
				alert ( successful ? _("The email address copied to the clipboard.") : text )
			} catch (err) {
				console.log('Oops, unable to copy');
			}
			$(textArea).remove();
		}
	}
	
	PageScript.prototype.initialise = function(text) {
		self.ajaxget("locale/hu.json",self.callback(self.initGettext, function(status, response){
			_=function(str){return str}
			self.displayServerResponse(response, {ok: self.init_})
		} ),true)
		window.traces.push("initialise")
	}
	
	PageScript.prototype.userNotLoggedIn = function( response ) {
		var data = self.validateServerMessage( response );
		if (data.errors && data.errors[0]!="no authorization") self.displayMsg(self.processErrors(data));
		self.refreshTheNavbar()
		if (self.QueryString.section) {
			if (self.QueryString.section!="all") self.displayTheSection(self.QueryString.section);
			else return;
		}
		else self.displayTheSection();
	}
	
	PageScript.prototype.userIsLoggedIn = function(text) {
		var data = JSON.parse(text);
		self.isLoggedIn=true
		self.refreshTheNavbar()
		self.ajaxget('/v1/getmyapps', self.myappsCallback)
		if (data.assurances.hashgiven && data.assurances.emailverification) {
			self.ajaxget("assurers.json", self.callback(self.fillAssurersTable), true)
		}
		if (data.assurances) {
			document.getElementById("me_Data").innerHTML=self.parseUserdata(data);
			document.getElementById("me_Settings").innerHTML=self.parseSettings(data);
			document.getElementById("assurance-giving_assurance_selector").innerHTML=self.parseAssurances(data);
			if (!(data.assurances.assurer)) self.isAssurer=false;
			else {
				self.isAssurer=true;
			}
		}

		if (self.QueryString.section) {
			if (self.QueryString.section!="all") self.displayTheSection(self.QueryString.section);
			else return;
		}
		else self.displayTheSection();
		window.traces.push('userIsLoggedIn')
	}

	
	PageScript.prototype.modNavbarItem=function(){
		document.getElementById("")
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
		window.traces.push("MSGbox ready")
	}

	PageScript.prototype.closePopup = function(popupCallback) {
		this.popupCallback=popupCallback //only for testing
		document.getElementById("PopupWindow_TitleDiv").innerHTML   = "";
		document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
		document.getElementById("PopupWindow_MessageDiv").innerHTML    = "";
		document.getElementById("PopupWindow_SuccessDiv").innerHTML = "";
		if (popupCallback) popupCallback();
		window.traces.push("popup closed")
		return "closePopup";
	}

	PageScript.prototype.init_=function(){
		if (self.QueryString.section){
			switch (self.QueryString.section) {
				case "email_verification":
					if (self.QueryString.secret) self.verifyEmail()
					break;
				case "emailchange":
					if (self.QueryString.email) {
						document.getElementById("emailchange_email").innerHTML=self.QueryString.email
					}
					break;
				case "cancelemailchange":
					if (self.QueryString.secret) self.cancelEmailChange()
					break;
			}
		}
		self.ajaxget("/v1/users/me", self.callback(self.userIsLoggedIn, self.userNotLoggedIn))	
		window.traces.push("init_")		
	}
	
	PageScript.prototype.verifyEmail=function() {
		var target   = document.getElementById("email_verification_message").innerHTML
		this.success = function(text){
			target=_("Your email validation was succesfull.")
		}
		this.error   = function(status,text){
			var data=JSON.parse(text);
			target=_("Your email validation <b>failed</b>.<br/>The servers response: ")+_(data.errors[0])
		}
		self.ajaxget( "/v1/verify_email/" + self.QueryString.secret, self.callback(this.succes,this.error) )
	}

	PageScript.prototype.changeEmail=function(confirm) {
		var data={
			confirm: confirm,
			secret: self.QueryString.secret
		}
		this.success=function(text){self.displayMsg({title:"Üzi",error:text})}
		self.ajaxpost( "/v1/confirmemailchange", data, self.callback(this.success) )
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
        email = pageScript.mailRepair(email);
		if (email=="") { self.displayMsg({title:"Hiba",error:"nem adtad meg az email címet"})}
		else {
			email = encodeURIComponent(email)
			self.ajaxget("/v1/user_by_email/"+email, self.callback(self.myCallback))
		}
	}
	
	PageScript.prototype.addAssurance = function() {
		if ( $("#assurance-giving_submit-button").hasClass("inactive") ) return;
	    digest = document.getElementById("assurancing_digest_input").value;
	    assurance = document.getElementById("assurance-giving_assurance_selector").value;
	    email = document.getElementById("ByEmailForm_email_input").value;
        email = pageScript.mailRepair(email);
	    csrf_token = self.getCookie('csrf');
	    data= {
	    	digest: digest,
	    	assurance: assurance,
	    	email: email,
	    	csrf_token: csrf_token
	    }
	    self.ajaxpost("/v1/add_assurance", data, self.callback(self.myCallback))
	}

/*
********************************
**    Adding credentials      **
********************************
*/	

	PageScript.prototype.addCredential = function(credentialType, identifier, secret) {
		console.log("addCredential:"+credentialType)
		var data = {
			credentialType: credentialType,
			identifier: identifier,
			password: secret
		}
		self.ajaxpost("/v1/add_credential", data, self.callback(self.userIsLoggedIn))
	}
	
	PageScript.prototype.addPasswordCredential = function(){
		var identifier=document.getElementById("AddPasswordCredentialForm_username_input").value;
		var secret=document.getElementById("AddPasswordCredentialForm_password_input").value;
		self.addCredential("password", identifier, secret);
	}
	
	PageScript.prototype.add_facebook_credential = function( FbUserId, FbAccessToken) {
		self.addCredential("facebook", FbUserId, FbAccessToken);
	}
/*	
	PageScript.prototype.addGoogleCredential = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addGithubCredential = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addTwitterCredential = function(){
		self.displayMsg({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
*/	
/*
********************************
**      Change settings       **
********************************
*/

	PageScript.prototype.changeHash = function() {
	    var digest = document.getElementById("change-hash-form_digest_input").value,
			csrf_token = self.getCookie('csrf'),
			data= {
				digest: digest,
				csrf_token: csrf_token
			}
	    self.ajaxpost("/v1/users/me/update_hash", data, self.callback(self.changeHashCallback))
	}	
	
	PageScript.prototype.changeHashCallback = function(text) {
		var msg=self.processErrors(JSON.parse(text))
		msg.callback=function(){
			self.get_me()
			self.viewChangeHashContainer()
			}
		self.displayMsg(msg)
	}
	
	PageScript.prototype.viewChangeHashForm = function() {
		document.getElementById("change-hash-form_hash-changer").style.display="table-row";
		document.getElementById("change-hash-form_hash-changer-buttons").style.display="table-row";
		document.getElementById("change-hash-form_hash-container").style.display="none";
		window.traces.push("viewChangeHashForm")
	}
	
	PageScript.prototype.viewChangeHashContainer = function() {
		document.getElementById("change-hash-form_hash-changer").style.display="none";
		document.getElementById("change-hash-form_hash-changer-buttons").style.display="none";
		document.getElementById("change-hash-form_hash-container").style.display="table-row";
	}
	
	PageScript.prototype.showHashChanger = function(){
		document.getElementById('change-hash-form_code-generation-input').style.display='block'
	}
	
	PageScript.prototype.hideHashChanger = function(){
		document.getElementById('change-hash-form_code-generation-input').style.display="none";
		window.open(self.QueryString.uris.ANCHOR_URL)
	}
	

	
/*
********************************
** My account section content **
********************************

/***** Settings tab *****/
	PageScript.prototype.parseSettings = function(data) {
		$("#ChangeEmailAddressForm_email_input").val(data.email)	
		$("#change-hash-form_digest-code").text(data.hash||"-- nincs megadva --")
		var result = '<h4><b>'+_("My credentials")+'</b></h4>\
		<table class="multiheader">';
		var c={	pw:[_("Password"),"password","document.getElementById('change-email_form').style.display='table-row'",true],
				fb:["Facebook","facebook","facebook.add_fb_credential()",false]}
/*				,
				git:["Github","github","pageScript.addGithubCredential()",false],
				tw:["Twitter","twitter","pageScript.addTwitterCredential()",false],
				go:["Google+","google","pageScript.addGoogleCredential()",false]
				};*/
		var credential_list = ""
		for( var i in c) {
			credential_list=(i=='pw')?'\
			<tr id="change-email_form">\
				<td>\
					<div class="form-level">\
					<input class="input-block" name="username" type="text" autocapitalize="off" placeholder="Felhasználónév" id="AddPasswordCredentialForm_username_input">\
					<span class="form-icon_"><i class="fa fa-envelope-o"></i>/<i class="fa fa-user"></i></span>\
					</div>\
					<div class="form-level">\
					<input class="input-block" type="password" placeholder="Jelszó" id="AddPasswordCredentialForm_password_input">\
					<span class="form-icon_"><i class=" fa fa-lock"></i></span>\
					</div>\
				</td>\
				<td class="button-container">\
					<a onclick="javascript:pageScript.addPasswordCredential()" class="btn btn_ fa fa-save" title="'+_("save")+'"></a>\
					<a onclick="javascript:document.getElementById(\'change-email_form\').style.display=\'none\'" class="btn btn_ fa fa-times" title="'+_("cancel")+'"></a>\
				</td>\
			</tr>\
			':"";
			for(var j=0; j<data.credentials.length; j++) {
				if (data.credentials[j].credentialType==c[i][1]) {
				credential_list += '\
			<tr>\
				<td><pre class="credential-item" id="Credential-Item-'+j+'_identifier">'+data.credentials[j].identifier+'</pre></td>\
				<td class="button-container">\
					<a onclick="javascript:pageScript.RemoveCredential(\'Credential-Item-'+j+'\').doRemove(\''+c[i][1]+'\')" class="btn btn_ fa fa-trash"></a>\
				</td>\
			</tr>'
				}
			}
			var credential_header='\
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
		</table>'
		return result;		
	}	

	PageScript.prototype.callSetAppCanEmailMe=function(app){
		var value=document.getElementById("application-allow-email-me-"+app).checked
		self.setAppCanEmailMe(app,value,self.myCallback)
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
					onclick="javascript: pageScript.callSetAppCanEmailMe('+app+')">\
				</td>\
			</tr>'
			}	
		}
		applist +='\
		</table>';
		document.getElementById("me_Applications").innerHTML=applist;
		window.traces.push("myappsCallback")
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
	
	PageScript.prototype.changeEmailAddress = function() {
	    var email = self.mailRepair(document.getElementById("ChangeEmailAddressForm_email_input").value);
		if (email=="") self.displayMsg({error:"<p class='warning'>Nincs megadva érvényes e-mail cím</p>"});
		else {
			var csrf_token = self.getCookie('csrf'),
				data= {
				newemail: email,
				csrf_token: csrf_token
			}
			self.ajaxpost('/v1/emailchange',data, self.callback(self.changeEmailCallback) )
		}	
	}
	
	PageScript.prototype.changeEmailCallback = function(text) {
		self.displayMsg(self.processErrors(JSON.parse(text)))
	}
	
	PageScript.prototype.deleteHash = function() {
		document.getElementById("change-hash-form_digest_input").value=""
		self.changeHash();
	}
	
	PageScript.prototype.emailChangeEditButton_onclick = function() {
		document.getElementById("ChangeEmailAddressForm_email_input").value=""
		document.getElementById("ChangeEmailAddressForm_email_input").placeholder=_("Type your new email address here")
	}
	
	PageScript.prototype.emailChangeInput_onkeyup = function(){
		var rgx_email   = new RegExp(/^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$/i);
		var inputField = document.getElementById("ChangeEmailAddressForm_email_input")
		if (rgx_email.exec(inputField.value)) {
			self.activateButton("changeEmil_saveButton", self.changeEmailAddress)
		}
		else self.deactivateButton("changeEmil_saveButton")
	}
	
// User actions	
	PageScript.prototype.InitiateResendRegistrationEmail = function() {
		self.ajaxget( "/v1/send_verify_email", self.callback() )
	}
	
	PageScript.prototype.initiateDeregister = function() {
		self.ajaxpost( "/v1/deregister", { csrf_token: self.getCookie("csrf") }, self.callback()  )
	}

	PageScript.prototype.doDeregister = function() {
		
		var deregisterCallback = function( response ) {
			self.isLoggedIn = false
			self.refreshTheNavbar();
			if ( self.page == "account" ) self.displayTheSection( "login" );
			self.displayServerResponse( response, {ok: self.doLoadHome} )
		}
		
		if ( document.getElementById("accept_deregister").checked ) {
			if ( self.QueryString.secret ) {
				var post = {
					csrf_token: self.getCookie("csrf"),
					deregister_secret: self.QueryString.secret
				}
				self.ajaxpost( "/v1/deregister_doit", post, self.callback( deregisterCallback ) )
			}
			else self.displayMsg({
					title:_("Error message"),
					error:_("The secret is missing")
			})
		}
		else self.displayMsg({
			title:_("Error message"),
			error:_("To accept the terms please mark the checkbox!")
		})			
	}
	
}()
)
