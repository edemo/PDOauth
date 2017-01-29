import x from './modules/back_to_top' //back to top button
import { _ } from './modules/gettext'
import { gettext } from './modules/gettext'
import PageScript from './modules/script.js'
import { setup_the_deregister_form_buttons } from './modules/setup_buttons'

var pageScript = new PageScript(),
	$this=pageScript
	
PageScript.prototype.page = "deregistration";

PageScript.prototype.main = function() {
	$this.ajaxget("/adauris", $this.callback($this.commonInit), true)
	setup_the_deregister_form_buttons($this)
	window.traces.push("main end")
}
	
PageScript.prototype.initialise = function(text) {
	var dictionaryLoadedCallback = function(response){
			gettext.initGettext(response)
			$this.init_()
		},
		dictionaryFailureCallback = function(response){
			gettext.mockGettext()
			$this.displayServerResponse(response, {ok: $this.init_})
	}	
	$this.ajaxget("locale/hu.json",$this.callback( dictionaryLoadedCallback, dictionaryFailureCallback ),true)
	window.traces.push("initialise")
}

PageScript.prototype.init_=function(){
	$this.ajaxget("/v1/users/me", $this.callback($this.userIsLoggedIn, $this.userNotLoggedIn))	
	window.traces.push("init_")		
}

PageScript.prototype.userIsLoggedIn = function( response ) {
	$this.isLoggedIn=true
	$this.refreshTheNavbar()
	window.traces.push('userIsLoggedIn')
}
	
PageScript.prototype.userNotLoggedIn = function( response ) {
	var data = $this.validateServerMessage( response );
	if (data.errors && data.errors[0]!="no authorization") $this.displayMsg($this.processErrors(data));
	$this.refreshTheNavbar()
}
	
PageScript.prototype.displayMsg = function( msg ) {
	if (!(msg.title || msg.error || msg.message || msg.success)) return
	$("#myModal").modal();
	if (!msg.callback) msg.callback="";
	$this.msgCallback=msg.callback; //only for testing
	document.getElementById("PopupWindow_CloseButton1").onclick = function() {$this.closePopup(msg.callback)}
	document.getElementById("PopupWindow_CloseButton2").onclick = function() {$this.closePopup(msg.callback)}
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
	$this.popupCallback=popupCallback //only for testing
	document.getElementById("PopupWindow_TitleDiv").innerHTML   = "";
	document.getElementById("PopupWindow_ErrorDiv").innerHTML   = "";
	document.getElementById("PopupWindow_MessageDiv").innerHTML    = "";
	document.getElementById("PopupWindow_SuccessDiv").innerHTML = "";
	if (popupCallback) popupCallback();
	window.traces.push("popup closed")
	return "closePopup";
}

PageScript.prototype.doDeregister = function() {
		
	var deregisterCallback = function( response ) {
		$this.isLoggedIn = false
		$this.refreshTheNavbar();
		$this.displayServerResponse( response, {ok: $this.doLoadHome} )
	}
		
	if ( document.getElementById("accept_deregister").checked ) {
		if ( $this.QueryString.secret ) {
			var post = {
				csrf_token: $this.getCookie("csrf"),
				deregister_secret: $this.QueryString.secret
			}
			$this.ajaxpost( "/v1/deregister_doit", post, $this.callback( deregisterCallback ) )
		}
		else $this.displayMsg({
				title:_("Error message"),
				error:_("The secret is missing")
		})
	}
	else $this.displayMsg({
		title:_("Error message"),
		error:_("To accept the terms please mark the checkbox!")
	})			
}


$(document).ready(pageScript.main)
	
