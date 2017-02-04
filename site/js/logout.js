import * as ajax from './modules/ajax.js';

var	c,
	getCookie = function(cname) {
		var name = cname + "=",
			ca = window.document.cookie.split(';');
		for(var i=0; i<ca.length; i++) {
			var c = ca[i];
			while (c.charAt(0)==' ') c = c.substring(1);
			if (c.indexOf(name) == 0) {
				return c.substring(name.length,c.length);
			}
		}
		return false;
	},
	tracker = document.getElementById("flag"),		// for testing
	next = function(){ tracker.style.display = "block"	}
if ( !(c=getCookie("sso_no_app_logout")) || c=="true" ) ajax.get( "/v1/logout", {next:next, error:next} )
else next();