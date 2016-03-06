(function(){	
	var self;
	PageScript.prototype.page = "blog";

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
}()
)