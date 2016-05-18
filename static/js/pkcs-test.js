(function(){	
	var self;
	PageScript.prototype.page = "pkcs10";

	PageScript.prototype.main = function() {
		self=this.getThis()
		self.ajaxget( "/adauris", self.callback(self.commonInit) )
	}

	PageScript.prototype.initialise = function() {
	}

	PageScript.prototype.keygen = function(formName) {
		var stringPEM = document.getElementById("pem-text-block").value;
		self.ajaxpost("/v1/ca/signreq", {pubkey: stringPEM, email:"gypeng@drezina.hu", createUser: false}, self.callback(self.keygenCallback))
	}
	
	PageScript.prototype.keygenCallback = function() {
		console.log("Keygencallback")
	}
	

}()
)
