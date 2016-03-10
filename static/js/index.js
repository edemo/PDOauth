(function(){	
	var self;
	PageScript.prototype.page = "index";

	PageScript.prototype.main = function() {
		self=this.getThis()
		this.ajaxget("/adauris", this.uriCallback)

	}

	PageScript.prototype.uriCallback = function(status,text) {
		var data = JSON.parse(text);
		xxxx=self;
		if (status==200) {
			self.QueryString.uris = data
			self.uribase = self.QueryString.uris.BACKEND_PATH;
			loc = '' + win.location
			if (loc.indexOf(self.QueryString.uris.SSL_LOGIN_BASE_URL) === 0) {
				self.ajaxget(self.QueryString.uris.SSL_LOGIN_BASE_URL+self.uribase+'/v1/ssl_login',pageScript.initCallback, true)
			}
			self.ajaxget("/v1/users/me", self.initCallback)
			self.getStatistics()
		}
		else self.displayMsg(self.processErrors(data));
	}
	
	PageScript.prototype.initCallback = function(status, text) {
		self.isLoggedIn=(status == 200)
		self.refreshTheNavbar()
	}
	
	PageScript.prototype.getStatistics=function(){
		this.ajaxget("/v1/statistics", self.statCallback)
	}
	
	PageScript.prototype.statCallback=function(status, text) {
		data=JSON.parse(text)
		if (data.error)	self.displayError();
		else {
				document.getElementById("user-counter").innerHTML=(data.users)?data.users:0
				document.getElementById("magyar-counter").innerHTML=(data.assurances.magyar)?data.assurances.magyar:0
				document.getElementById("assurer-counter").innerHTML=(data.assurances.assurer)?data.assurances.assurer:0
				document.getElementById("application-counter").innerHTML=(data.applications)?data.applications:0
			
		}
	}
}()
)