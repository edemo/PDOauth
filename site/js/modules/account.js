import PageScript from './script'
import { _ } from './gettext'
import { gettext } from './gettext'
import { setup_the_navbar_buttons_onclick_account } from './setup_buttons'
import { setup_the_registration_form_buttons } from './setup_buttons'
import { setup_the_login_form_buttons } from './setup_buttons'
import { setup_the_assurancing_form_buttons } from './setup_buttons'
import { setup_the_mysettings_form_buttons } from './setup_buttons'
import { setup_email_verification_form_buttons } from './setup_buttons'
//import { setup_reset_password_form_buttons } from './setup_buttons'
import { setup_email_change_form_buttons} from './setup_buttons'
import * as Control from './control'
import * as Cookie from './cookie'
import * as Msg from './messaging'
import * as Digest from './digest'
import * as Ajax from './ajax.js'

export var pageScript = new PageScript()

var self = pageScript
 
Msg.setTarget('popup')

PageScript.prototype.page = "account";
PageScript.prototype.main = function() {
	self.commonInit()
	setup_the_registration_form_buttons(self)
	setup_the_login_form_buttons(self)
	setup_the_assurancing_form_buttons(self)
	setup_the_mysettings_form_buttons(self)
	setup_email_verification_form_buttons(self)
//	setup_reset_password_form_buttons(self)
	setup_email_change_form_buttons(self)
	var section = self.QueryString.section
	switch (section) {
		case "all" :
		[].forEach.call( document.getElementsByClassName("func"), function (e) { e.style.display="block"; } );
			break;
		case "registration" :
			self.QueryString.section="register"
			Control.show(self.QueryString.section+"_section")
			break;
		case "account" :
			self.QueryString.section="my_account"
			Control.show(self.QueryString.section+"_section")
			break;
		case "pwreset" :
			self.QueryString.section="password_reset"
			Control.show(self.QueryString.section+"_section")
			if (self.QueryString.secret) {
				document.getElementById("PasswordResetForm_secret_input").value=self.QueryString.secret
			}
			break;
		case "deregistration" :
			self.QueryString.section="deregistration"
			Control.show(self.QueryString.section+"_section")
			break;
		case "emailcheck" :
			self.QueryString.section="email_verification"
			Control.show(self.QueryString.section+"_section")
			break;
		case "cancelemailchange" :
			self.QueryString.section="cancelemailchange"
			Control.show(self.QueryString.section+"_section")
			break;
		case "emailchange" :
			self.QueryString.section="emailchange"
			Control.show(self.QueryString.section+"_section")
			break;
		case "login" :
			Control.show(section+"_section")
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
		Ajax.get( "locale/hu.json", { 
			next: self.gettextCallback,
			error: function(response){
					gettext.mockGettext()
					self.displayServerResponse(response, {ok: self.init_})
				}
			}, true )
		window.traces.push("initialise")
	}
	
	PageScript.prototype.gettextCallback = function(response){
		gettext.initGettext(response)
		self.init_()
	} 
	
	PageScript.prototype.userNotLoggedIn = function( response ) {
		var data = self.validateServerMessage( response );
		if (data.errors && data.errors[0]!="no authorization") Msg.display(self.processErrors(data));
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
		Ajax.ajaxget( '/v1/getmyapps', self.myappsCallback)
		
		if (data.assurances.hashgiven && data.assurances.emailverification) {
			Ajax.get( "assurers.json", { next: self.fillAssurersTable }, true)
		}
		
		Control.innerHTML( "me_Data", self.parseUserdata( data ) )	
		$("#change-hash-form_digest-code").text( data.hash || "-- nincs megadva --" )
		
		if (data.assurances) {
			if (!(data.assurances.assurer)) self.isAssurer=false;
			else {
				self.isAssurer=true;
				Control.innerHTML( "assurance-giving_assurance_selector", self.parseAssurances( data ) )
			}
		}
		
		if (data.credentials) {
			self.parseCredentials( data ) 
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
		Ajax.get( "/v1/users/me", { next: self.userIsLoggedIn, error: self.userNotLoggedIn } )	
		window.traces.push("init_")		
	}
	
	PageScript.prototype.verifyEmail=function() {
		var target   = document.getElementById("email_verification_message").innerHTML,
			onsuccess = function(text){
				target=_("Your email validation was succesfull.")
			},
			onerror   = function(text){
				var data=JSON.parse(text);
				target=_("Your email validation <b>failed</b>.<br/>The servers response: ")+_(data.errors[0])
			}
		Ajax.get( "/v1/verify_email/" + self.QueryString.secret, { next: onsucces, error: onerror } )
	}

	PageScript.prototype.changeEmail=function(confirm) {
		var data={
				confirm: confirm,
				secret: self.QueryString.secret
			}
		Ajax.post( "/v1/confirmemailchange", data, {} )
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
	    var email = self.mailRepair( Control.getValue( "ByEmailForm_email_input" ) );
		if (email=="") { 
			Msg.display( {
				title:"Hiba",
				error:"nem adtad meg az email címet" 
			} )
		}
		else {
			email = encodeURIComponent(email)
			Ajax.get( "/v1/user_by_email/"+email, { next: self.myCallback } )
		}
	}
	
	PageScript.prototype.addAssurance = function() {
		if ( $("#assurance-giving_submit-button").hasClass("inactive") ) return;
	    var data= {
		    	digest: document.getElementById("assurancing_digest_input").value,
		    	assurance: document.getElementById("assurance-giving_assurance_selector").value,
		    	email: self.mailRepair(document.getElementById("ByEmailForm_email_input").value),
	  		  	csrf_token: Cookie.get('csrf')
		    }
	    Ajax.post( "/v1/add_assurance", data, { next: self.myCallback } )
	}

/*
********************************
**    Adding credentials      **
********************************
*/	

	PageScript.prototype.addCredential = function( credentialType, identifier, secret ) {
		var data = {
			credentialType: credentialType,
			identifier: identifier,
			password: secret
		}
		Ajax.post( "/v1/add_credential", data, { next: self.userIsLoggedIn } )
	}
	
	PageScript.prototype.addPasswordCredential = function(){
		var identifier = Control.getValue( "AddPasswordCredentialForm_username_input" ),
			secret = Control.getValue( "AddPasswordCredentialForm_password_input" )
		self.addCredential( "password", identifier, secret );
	}
	
	PageScript.prototype.add_facebook_credential = function( FbUserId, FbAccessToken) {
		self.addCredential( "facebook", FbUserId, FbAccessToken );
	}
/*	
	PageScript.prototype.addGoogleCredential = function(){
		Msg.display({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addGithubCredential = function(){
		Msg.display({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
	
	PageScript.prototype.addTwitterCredential = function(){
		Msg.display({title:_("Under construction"), error:_("This function is not working yet.")});	
	}
*/	
/*
********************************
**      Change settings       **
********************************
*/

	PageScript.prototype.changeHash = function( noMessage ) {
		var next = noMessage ? function(){} : self.changeHashCallback,
			data= {
				digest: Control.getValue("change-hash-form_digest_input"),
				csrf_token: Cookie.get('csrf')
			}
	    Ajax.post( "/v1/users/me/update_hash", data, { next:next } )
	}	
	
	PageScript.prototype.changeHashCallback = function(text) {
		var msg=self.processErrors(JSON.parse(text))
		msg.callback=function(){
			self.get_me()
			self.viewChangeHashContainer()
			}
		Msg.display(msg)
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
	PageScript.prototype.parseCredentials = function(data) {
		Control.setValue( "ChangeEmailAddressForm_email_input", data.email )
		var div = $( '#myCredentials' ).empty(),
			table = $( '<table class="multiheader"></table>' ),
			c={	pw:[_("Password"), "password", function(){document.getElementById('AddPasswordCredentialForm').style.display='table-row'}, true],
				fb:["Facebook", "facebook", facebook.add_fb_credential, false]
/*
				git:["Github","github","pageScript.addGithubCredential()",false],
				tw:["Twitter","twitter","pageScript.addTwitterCredential()",false],
				go:["Google+","google","pageScript.addGoogleCredential()",false]
*/
				},
			addPasswordCredentialForm='\
			<tr id="AddPasswordCredentialForm" style="display:none">\
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
					<a id="AddPasswordCredentialForm_doit-button" class="btn btn_ fa fa-save" title="'+_("save")+'"></a>\
					<a id="AddPasswordCredentialForm_cancel-button" class="btn btn_ fa fa-times" title="'+_("cancel")+'"></a>\
				</td>\
			</tr>\
			',
			PlusButton = '<a class="btn fa fa-plus"></a>',
			TrashButton = '<a class="btn btn_ fa fa-trash"></a>',
			th = '<th></th>',
			tr = '<tr></tr>'
			
		$( div ).append( $( '<h4><b>' + _( "My credentials" ) + '</b></h4>' ) )
		console.log(data.credentials)
		for( var i in c ) {
			// credential header
			console.log(i)
			var credential_header = $( tr ),
				headerButtonContainer = $( th )
			$( credential_header ).id = i + '-credential-list'
			$( credential_header ).append( $('<th>'+c[i][0]+'</th>') )
			if (c[i][3]){
				var theAddButton = $( PlusButton )
				$( theAddButton ).on( "click", c[i][2] )
				$( headerButtonContainer ).append( $( theAddButton ) )
				
			}
			$( credential_header ).append( $( headerButtonContainer ) )
			$( table ).append( credential_header ) 
			if (i=='pw') $( table ).append( $( addPasswordCredentialForm ) )
				
			// credential list
			for( var j=0; j<data.credentials.length; j++ ) {
				if (data.credentials[j].credentialType==c[i][1]) {
					
					var theCredential = $( tr ),
						theDeleteButton = $( TrashButton )
					$( theCredential ).append( $( '<td><pre class="credential-item" id="Credential-Item-' + j + '_identifier">' + data.credentials[j].identifier + '</pre></td>' ) )
					$( theDeleteButton ).attr( 'identifier', data.credentials[j].identifier )
					$( theDeleteButton ).attr( 'cr-type', c[i][1] )
					$( theDeleteButton ).on( "click", function(){ self.RemoveCredential( this ) } )
					$( theCredential ).append( $( '<td class="button-container"></td>' ).append( $( theDeleteButton ) ) )
					$( table ).append( theCredential ) 
				}
			}
		}
		$( div ).append( $( table ) ) 
		document.getElementById("AddPasswordCredentialForm_doit-button").onclick = self.addPasswordCredential
		document.getElementById("AddPasswordCredentialForm_cancel-button").onclick = function(){ Control.hide( 'AddPasswordCredentialForm' ) }	
	}	

	PageScript.prototype.callSetAppCanEmailMe = function(app){
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
		for( var app in self.aps){ 
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
		var selector = '',
			text
		for(var ass in data.assurances) {
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
		if (email=="") Msg.display({error:"<p class='warning'>Nincs megadva érvényes e-mail cím</p>"});
		else {
			var csrf_token = Cookie.get('csrf'),
				data= {
				newemail: email,
				csrf_token: csrf_token
			}
			Ajax.post( '/v1/emailchange', data, { next: self.changeEmailCallback } )
		}	
	}
	
	PageScript.prototype.changeEmailCallback = function(text) {
		Msg.display(self.processErrors(JSON.parse(text)))
	}
	
	PageScript.prototype.deleteHash = function() {
		Msg.display({ 	title: _("Caution!!"),
						message: _("Do you want realy delete your secret code? Your assurances will be deleted as well!!"),
						ok: function() {
								$('#myModal').on('hidden.bs.modal', function() {
									Control.setValue( "change-hash-form_digest_input", "" )
									self.changeHash( true );
								})
							}
					})
	}
	
	PageScript.prototype.emailChangeEditButton_onclick = function() {
		Control.setValue( "ChangeEmailAddressForm_email_input", "" )
		document.getElementById("ChangeEmailAddressForm_email_input").placeholder=_("Type your new email address here")
	}
	
	PageScript.prototype.emailChangeInput_onkeyup = function(){
		var rgx_email = new RegExp(/^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$/i);
		if ( rgx_email.exec( Control.getValue( "ChangeEmailAddressForm_email_input" ) ) ) {
			Control.activate( "changeEmil_saveButton", self.changeEmailAddress )
		}
		else Control.deactivate( "changeEmil_saveButton" )
	}
	
// User actions	
	PageScript.prototype.InitiateResendRegistrationEmail = function() {
		Ajax.get( "/v1/send_verify_email", {} )
	}
	
	PageScript.prototype.initiateDeregister = function() {
		Ajax.post( "/v1/deregister", { csrf_token: Cookie.get("csrf") }, {}  )
	}

