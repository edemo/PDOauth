import PageScript from './script'
import { setup_the_navbar_buttons_onclick } from './setup_buttons'
import * as Ajax from  './ajax'
export var pageScript = new PageScript();
	
	var self=pageScript
	
	PageScript.prototype.page = "index";

	PageScript.prototype.main = function() {
		self.commonInit()
	}

	PageScript.prototype.initialise = function() {
		Ajax.ajaxget("/v1/users/me", self.initCallback)
		if (document.getElementById("counter_area")) self.getStatistics()
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		self.isLoggedIn = (status == 200)
		self.refreshTheNavbar()
	}
	
	PageScript.prototype.getStatistics=function(){
		Ajax.ajaxget("/v1/statistics", self.callback(self.statCallback))
	}
	
	PageScript.prototype.statCallback=function(text) {
		var data=JSON.parse(text)
		document.getElementById("user-counter").innerHTML=(data.users)?data.users:0
		document.getElementById("magyar-counter").innerHTML=(data.assurances.magyar)?data.assurances.magyar:0
		document.getElementById("assurer-counter").innerHTML=(data.assurances.assurer)?data.assurances.assurer:0
		document.getElementById("application-counter").innerHTML=(data.applications)?data.applications:0
		//init counter if data presents
		$('.counter').counterUp({
			delay: 100,
			time: 2000
		});
	}
