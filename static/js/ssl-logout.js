(function(){	
	var self;

	PageScript.prototype.logout_ssl = function() {
		self=this.getThis()
		this.ajaxget("/adauris", this.logoutSSLCallback)

	}

	PageScript.prototype.logoutSSLCallback = function(status,text) {
		self.data = JSON.parse(text);
		xxxx=self;
		if (status==200) {
			self.ajaxget("https://sso.edemokraciagep.org:8080/ssl_logout/", self.testCallback);
		}
		else self.displayMsg(self.processErrors(data));
	}
	
	PageScript.prototype.testCallback = function(status, text) {
		console.log("callback:"+status+","+text)
		setTimeout(function()
		    {
				window.location = self.data.START_URL
		    }, 2000);
	}
}()
)
