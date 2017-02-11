// password reset functions
import * as Ajax from './ajax'
import * as Msg from './messaging'
import * as Control from './control'

Msg.setTarget('popup')

var secret

export function setSecret(theSecret){
	secret=theSecret
}

export function	doit() {
	var password = document.getElementById("PasswordResetForm_password_input").value;
	ajax.post("/v1/password_reset", {secret: pwReset_Secret, password: password}, { next:self.reloadCallback} )
}
	
export function	initiate( formName ) {
	var email = self.mailRepair(Control.getValue( formName + "_email_input"))
	if ( email!="" ) Ajax.get("/v1/users/" + email + "/passwordreset", {next:self.myCallback});
	else {
		Msg.display({"title":"Hiba","error":"Nem adtál meg email címet"})
	}
}

export function setup_controlls(){
	document.getElementById("PasswordResetForm").onsubmit=function(){ doit(); return false }
	Control.setValue("PasswordResetForm_secret_input", secret )
}