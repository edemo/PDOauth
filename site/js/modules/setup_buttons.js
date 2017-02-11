import * as Cookie from './cookie'
import * as Password from './password'
import * as Digest from './digest'
import * as Control from './control'
import * as Msg from './messaging'

export function setup_the_navbar_buttons_onclick_account(ps){
	document.getElementById("nav-bar-login_a").onclick=function(){ps.displayTheSection('login')}
	document.getElementById("nav-bar-register_a").onclick=function(){ps.displayTheSection('register')}
	document.getElementById("nav-bar-my_account_a").onclick=function(){ps.displayTheSection('my_account')}	
	document.getElementById("logout_button").onclick=ps.logout	
}

export function	setup_the_navbar_buttons_onclick(ps) {
	document.getElementById("nav-bar-login_a").onclick=function(){ window.location='fiokom.html' }
	document.getElementById("nav-bar-register_a").onclick=function(){ window.location='fiokom.html?section=register' }
	document.getElementById("nav-bar-my_account_a").onclick=function(){ window.location='fiokom.html' }	
	document.getElementById("logout_button").onclick=ps.logout	
}

export function setup_the_deregister_form_buttons(ps){
	document.getElementById("deregistration-form_submit-button").onclick=ps.doDeregister
}

export function setup_the_registration_form_buttons(ps){
	document.getElementById("registration-form_submitButton").onclick=ps.doRegister
	document.getElementById("registration-form-method-selector-pw").onclick=function(){ps.setRegistrationMethode('pw')}
	document.getElementById("registration-form_getDigestButton").onclick=Digest.getter('registration-form').getDigest
	document.getElementById("registration-form_predigest_mothername").onkeyup=function(){Digest.refreshMonitor('registration-form_predigest')}
	document.getElementById("registration-form_predigest_input").onkeyup=function(){Digest.refreshMonitor('registration-form_predigest')}
	document.getElementById("registration-form-method-selector-pw").onclick=function(){ps.setRegistrationMethode('pw')}
	document.getElementById("create_myself").onclick=function() {
		document.getElementById('registration-form_code-generation-input').style.display='none'
	} 
	document.getElementById("make_here").onclick=function() {
		document.getElementById('registration-form_code-generation-input').style.display='block'
	}
	document.getElementById("registration-form_secret_input").onkeyup=function(){Password.changed('registration-form')}
	document.getElementById("registration-form_secret_backup").onkeyup=function(){Password.equal('registration-form')}
}
export function setup_the_login_form_buttons(ps){
	document.getElementById("loginform").onsubmit=function(){ps.login(); return false}
	document.getElementById("InitiatePasswordReset").onclick=function(){ps.InitiatePasswordReset('LoginForm')}
}
export function setup_the_assurancing_form_buttons(ps){
	document.getElementById("ByEmailForm_submitButton").onclick=ps.byEmail
	document.getElementById("assurance-giving_submit-button").onclick=ps.addAssurance
	document.getElementById("assurancing_getDigestButton").onclick=Digest.getter('assurancing').getDigest
	document.getElementById("assurancing_predigest_mothername").onkeyup=function(){Digest.refreshMonitor('assurancing_predigest')}
	document.getElementById("assurancing_predigest_input").onkeyup=function(){Digest.refreshMonitor('assurancing_predigest')}
	document.getElementById("create_myself").onclick=function() {Control.hide('registration-form_code-generation-input')} 
	document.getElementById("make_here").onclick=function() {Control.show('registration-form_code-generation-input')}
}
export function setup_the_mysettings_form_buttons(ps){
	document.getElementById("ChangeEmailAddressForm_email_input").onkeyup=ps.emailChangeInput_onkeyup
	document.getElementById("emailChangeEditButton").onclick=ps.emailChangeEditButton_onclick
	document.getElementById("changeEmil_saveButton").onclick=ps.changeEmailAddress
	document.getElementById("viewChangeHashForm").onclick=ps.viewChangeHashForm
	document.getElementById("deleteHashButton").onclick=ps.deleteHash
	document.getElementById("change-hash-form_view-container").onclick=ps.viewChangeHashContainer
	document.getElementById("changeHash").onclick=ps.changeHash
	document.getElementById("change-hash-form_getDigestButton").onclick=Digest.getter('change-hash-form', ps.changeHash).getDigest	
	document.getElementById("change-hash-form_predigest_mothername").onkeyup=function(){Digest.refreshMonitor('change-hash-form_predigest')}
	document.getElementById("change-hash-form_predigest_input").onkeyup=function(){Digest.refreshMonitor('change-hash-form_predigest')}
	document.getElementById("create_hash_myself").onclick=ps.hideHashChanger
	document.getElementById("create_hash_here").onclick=ps.showHashChanger
	document.getElementById("allow_app_sso_autologout").onclick=function(){Cookie.set("sso_no_app_logout", this.checked.toString(), 2000 )}
	document.getElementById("allow_app_sso_autologout").checked=Cookie.get("sso_no_app_logout")!="false"
	document.getElementById("initiate-deregister_button").onclick=function(){ps.initiateDeregister('userdata_editform')}
	document.getElementById("initiate-resendemail_button").onclick=ps.InitiateResendRegistrationEmail
}
export function setup_login_page_controlls(ps){
	document.getElementById("PopupWindow_CloseButton").onclick=Msg.closePopup
	document.getElementById("section_changer_register").onclick=function(){ps.showSection('register_section')}
	document.getElementById("loginform").onsubmit=function(){ps.login(); return false}
	document.getElementById("InitiatePasswordReset").onclick=function(){ps.InitiatePasswordReset('LoginForm')}
	document.getElementById("emailverification_button").onclick=function(){ps.showForm('emailverification')}
	document.getElementById("emailverification-input_button").onclick=ps.init_
	document.getElementById("emailverification-cancel_button").onclick=function(){ps.hideForm('emailverification')}
	document.getElementById("hashgiven_button").onclick=function(){ps.showForm('hashgiven')}
	document.getElementById("login_make-self").onclick=function(){Digest.getter('login').methodChooser('self')}
	document.getElementById("login_predigest_mothername").onkeyup=function(){Digest.refreshMonitor('login_predigest')}
	document.getElementById("login_predigest_input").onkeyup=function(){Digest.refreshMonitor('login_predigest')}
	document.getElementById("login_getDigestButton").onclick=Digest.getter('login').getDigest
	document.getElementById("code-generation-cancel_button").onclick=function(){ps.hideForm('hashgiven')}
	document.getElementById("code-generation-cancel_button_").onclick=function(){ps.hideForm('hashgiven')}
	var field=document.getElementById("login_digest_input")
	field.onclick=function(){ps.textareaOnKeyup(field)}	
	document.getElementById("acceptance_accept").onclick=function(){ps.acceptGivingTheData(true)}
	document.getElementById("acceptance_cancel").onclick=function(){ps.acceptGivingTheData(false)}
	document.getElementById("section_changer_login").onclick=function(){ps.showSection('login_section')}
	document.getElementById("registration-form-method-selector-pw").onclick=function(){ps.setRegistrationMethode('pw')}
	document.getElementById("registration-form-method-selector-fb").onclick=function(){ps.setRegistrationMethode('fb')}
	document.getElementById("registration-form_secret_input").onkeyup=function(){Password.changed('registration-form')}
	document.getElementById("registration-form_secret_backup").onkeyup=function(){Password.equal('registration-form')}
	document.getElementById("registration-form_make-self").onclick=function(){Digest.getter('registration-form').methodChooser('self')}
	document.getElementById("registration-form_predigest_mothername").onkeyup=function(){Digest.refreshMonitor('registration-form_predigest')}
	document.getElementById("registration-form_predigest_input").onkeyup=function(){Digest.refreshMonitor('registration-form_predigest')}
	document.getElementById("registration-form_getDigestButton").onclick=Digest.getter('registration-form').getDigest
	var field_=document.getElementById("registration-form_digest_input")
	field_.onclick=function(){ps.textareaOnKeyup(field_)}
	document.getElementById("registration-form_submitButton").onclick=ps.doRegister
}
export function setup_email_verification_form_buttons(ps){
	document.getElementById("email_verification_button").onclick=function(){ps.doRedirect('fiokom.html')}
}

export function setup_email_change_form_buttons(ps){
	document.getElementById("change-email-form_ok").onclick=function(){ps.changeEmail(true)}
	document.getElementById("change-email-form_cancel").onclick=function(){ps.changeEmail(false)}
}
