import x from './modules/back_to_top' //back to top button
import { _ } from './modules/gettext'		// gettext interface
import { gettext } from './modules/gettext' // gettext init class
import { setup_the_navbar_buttons_onclick } from './modules/setup_buttons'
import * as ajax from './modules/ajax'
import * as pwreset from './modules/pwreset'

function setup_controlls(){
	document.getElementById("PasswordResetForm").onsubmit=function(){ pwreset.doit(); return false }
}

	if (QueryString && QueryString.secret) pwreset.secret=QueryString.secret

var commonInit	
var main = function (){
	ajax.get("/adauris", {next: commonInit}, true)
	setup_the_navbar_buttons_onclick(self)
	window.traces.push("main end")
}
	
$( document ).ready( main )