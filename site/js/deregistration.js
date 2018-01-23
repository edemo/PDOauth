import x from './modules/back_to_top' //back to top button
import { _ } from './modules/gettext'
import { gettext } from './modules/gettext'
import PageScript from './modules/script.js'
import { setup_the_deregister_form_buttons } from './modules/setup_buttons'
import * as Ajax from './modules/ajax'
import * as Msg from './modules/messaging'
import * as Control from './modules/control'
import * as Cookie from './modules/cookie'
 
var pageScript = new PageScript(),
	$this=pageScript

Msg.setTarget('popup')
	
PageScript.prototype.page = "deregistration";

PageScript.prototype.main = function() {
	$this.commonInit()
	setup_the_deregister_form_buttons($this)
	window.traces.push("main end")
}
	
PageScript.prototype.initialise = function(text) {
	gettext.loadPo( 'hu', $this.init_ )
	window.traces.push("initialise")
}

PageScript.prototype.init_=function( success, response ){
	if (!success) $this.displayServerResponse( response )
	Ajax.get("/v1/users/me", {next: $this.userIsLoggedIn, error:$this.userNotLoggedIn})	
	window.traces.push("init_")		
}

PageScript.prototype.userIsLoggedIn = function( response ) {
	$this.isLoggedIn=true
	$this.refreshTheNavbar()
	window.traces.push('userIsLoggedIn')
}
	
PageScript.prototype.userNotLoggedIn = function( response ) {
	var data = $this.validateServerMessage( response );
	if (data.errors && data.errors[0]!="no authorization") Msg.display($this.processErrors(data));
	$this.refreshTheNavbar()
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
				csrf_token: Cookie.get("csrf"),
				deregister_secret: $this.QueryString.secret
			}
			Ajax.post( "/v1/deregister_doit", post, { next: deregisterCallback } )
		}
		else Msg.display({
				title:_("Error message"),
				error:_("The secret is missing")
		})
	}
	else Msg.display({
		title:_("Error message"),
		error:_("To accept the terms please mark the checkbox!")
	})			
}


$(document).ready(pageScript.main)
	
