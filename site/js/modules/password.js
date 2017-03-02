// password validation helpers
import { _ } from './gettext'

export function changed( formName ) {
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
		equal(formName)
	}
	
export function equal( formName ) {
		var pwInput=document.getElementById(formName+"_secret_input")
		var pwBackup=document.getElementById(formName+"_secret_backup")
		var pwEqual=document.getElementById(formName+"_pw-equal")
		if (pwInput.value==pwBackup.value) pwEqual.innerHTML = '<span style="color:green">'+_("OK.")+'</span>';	
		else pwEqual.innerHTML = '<span style="color:red">'+_("Passwords are not equal.")+'</span>';	
	}