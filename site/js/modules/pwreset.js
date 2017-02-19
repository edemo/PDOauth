// password reset functions
import PageScript from './script'
import * as Ajax from './ajax'
import * as Msg from './messaging'
import * as Control from './control'
import { _ } from './gettext'		// gettext interface
import { gettext } from './gettext' // gettext init class
import { setup_the_navbar_buttons_onclick } from './setup_buttons'
import { uris } from './adauris'

var self = new PageScript(),
	secret = self.QueryString.secret || "",
	userIsLoggedIn=function(){
		self.isLoggedIn=true
		self.refreshTheNavbar()		
	},
	userNotLoggedIn=function(){
		self.refreshTheNavbar()		
	}

export function	doit() {
	var password = Control.getValue("PasswordResetForm_password_input");
	Ajax.post("/v1/password_reset", {secret: secret, password: password}, {} )
}

export function setup_controlls(){
	document.getElementById("PasswordResetForm").onsubmit=function(){ doit(); return false }
	Control.setValue("PasswordResetForm_secret_input", secret )
}

export function main(){
	self.page="passwordreset"
	self.QueryString.uris = uris;
	Msg.setTarget('popup')
	gettext.loadPo( 'hu' )
	Ajax.get( "/v1/users/me", { next: userIsLoggedIn, error: userNotLoggedIn } )
	Control.show("password_reset_section")
	setup_controlls()
	setup_the_navbar_buttons_onclick(self)
	window.traces.push("main end")
}