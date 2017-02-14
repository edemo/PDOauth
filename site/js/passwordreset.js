import x from './modules/back_to_top' //back to top button
import { _ } from './modules/gettext'		// gettext interface
import { gettext } from './modules/gettext' // gettext init class
import { setup_the_navbar_buttons_onclick } from './modules/setup_buttons'
import * as pwreset from './modules/pwreset'

function setup_controlls(){
	document.getElementById("PasswordResetForm").onsubmit=function(){ pwreset.doit(); return false }
}

	if (QueryString && QueryString.secret) pwreset.setSecret(QueryString.secret)

var main = function (){
	gettext.loadPo( 'hu' )
	setup_the_navbar_buttons_onclick(self)
	window.traces.push("main end")
}
	
$( document ).ready( main )