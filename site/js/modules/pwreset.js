// password reset functions
import * as ajax from '/.ajax'

var secret

export function setSecret(theSecret){
	secret=theSecret
}

export function	doit() {
	var password = document.getElementById("PasswordResetForm_password_input").value;
	ajax.ajaxpost("/v1/password_reset", {secret: pwReset_Secret, password: password}, ajax.callback( self.reloadCallback ))
}
	
export function	initiate( formName ) {
	var emailInput = document.getElementById( formName + "_email_input")
	if ( emailInput!="" ) self.ajaxget("/v1/users/"+self.mailRepair(emailInput.value)+"/passwordreset", self.callback(self.myCallback));
	else {
		emailInput.className="missing";
		this.displayMsg({"title":"Hiba","error":"Nem adtál meg email címet"})
	}
}

export function setup_controlls(){
	document.getElementById("PasswordResetForm").onsubmit=function(){ doit(); return false }
	if (ps.QueryString && ps.QueryString.secret) document.getElementById("PasswordResetForm_secret_input").value=ps.QueryString.secret
}