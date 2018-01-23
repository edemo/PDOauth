import PageScript from './modules/script'
import * as ajax from './modules/ajax';
import * as cookie from './modules/cookie'
var pageScript = new PageScript()
//	alert(decodeURIComponent(pageScript.QueryString.next))
var	c,
	tracker = document.getElementById("flag"),		// for testing
	next = function(){ 
		if (pageScript.QueryString.next){
			window.location.href=decodeURIComponent(pageScript.QueryString.next) 
		}
	}
if ( !(c=cookie.get("sso_no_app_logout")) || c=="true" ) ajax.get( "/v1/logout", {next:next, error:next} )
else next();