export function setup_the_navbar_buttons_onclick(ps){
	console.log(ps)
	if (ps.page=="account") {
		document.getElementById("nav-bar-login_a").onclick=function(){ps.navigateToTheSection('login')}
		document.getElementById("nav-bar-register_a").onclick=function(){ps.navigateToTheSection('register')}
		document.getElementById("nav-bar-my_account_a").onclick=function(){ps.navigateToTheSection('my_account')}	
	}
	else {
		document.getElementById("nav-bar-login_a").onclick=function(){ps.doRedirect('fiokom.html')}
		document.getElementById("nav-bar-register_a").onclick=function(){ps.doRedirect('fiokom.html')}
		document.getElementById("nav-bar-my_account_a").onclick=function(){ps.doRedirect('fiokom.html')}	
	}
	document.getElementById("logout_button").onclick=ps.logout	
}
export function setup_the_deregister_form_buttons(ps){
	document.getElementById("deregistration-form_submit-button").onclick=ps.doDeregister
}
export function setup_the_registration_form_buttons(ps){
	document.getElementById("registration-form_submitButton").onclick=ps.doRegister
	document.getElementById("registration-form-method-selector-pw").onclick=function(){ps.setRegistrationMethode('pw')}
}
export function setup_the_login_form_buttons(ps){
	document.getElementById("loginform").onsubmit=function(){ps.login(); return false}
	document.getElementById("InitiatePasswordReset").onclick=ps.InitiatePasswordReset
}
