import * as ajax from './modules/ajax';
import * as cookie from './modules/cookie'
var	c,
	tracker = document.getElementById("flag"),		// for testing
	next = function(){ tracker.style.display = "block"	}
if ( !(c=cookie.get("sso_no_app_logout")) || c=="true" ) ajax.get( "/v1/logout", {next:next, error:next} )
else next();