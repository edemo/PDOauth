  window.fbAsyncInit = function() {
	  FB.init({
	    appId      : '517253418423328',
	    cookie     : true,  // enable cookies to allow the server to access 
	                        // the session
	    xfbml      : true,  // parse social plugins on this page
	    version    : 'v2.2' // use version 2.2
	  });
  };

  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

function FaceBook(pageScript) {
	this.pageScript = pageScript;
	this.doc = document;
	this.loggedIn = false;
}

  function statusChangeCallback(response) {
    if (response.status === 'connected') {
      testAPI();
    } else if (response.status === 'not_authorized') {
      document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    } else {
      document.getElementById('status').innerHTML = 'Please log ' +
        'into Facebook.';
    }
  }

  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }


  function testAPI() {
    FB.api('/me', function(response) {
      console.log('response: ' + DumpObjectIndented(response,' '));
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
  }

  
	FaceBook.prototype.credentialCallBack = function(response) {
  		var self = this;
	    if (response.status === 'connected') {
	    	self.loggedIn = response;
	    	self.pageScript.add_facebook_credential(response.authResponse.userID, response.authResponse.accessToken)
	    } else {
	    	self.doc.getElementById('AddCredentialForm_ErrorMsg').innerHTML = '<p class="warning">A facebook bejelentkezés sikertelen</p>';
	    } 
	  }

	FaceBook.prototype.add_fb_credential = function() {
		var self = this;
		if (! self.loggedIn ) {
//			FB.login(function(response) {
//			    self.credentialCallBack(response);
			self.getFbUser(self.credentialCallBack)
		};
	}
	
	FaceBook.prototype.getFbUser  =function(callback) {
		var self=this
		FB.getLoginStatus( function(resp){self.statusChangeCallback(resp,callback)})
	}
	
	FaceBook.prototype.statusChangeCallback = function(response,callback) {
		console.log(response)
		if (response.status === 'connected') {
			callback(response)
		} else if (response.status === 'not_authorized') {
			console.log('not_authorised')
		} else {
			console.log('login')
			FB.login(function(resp){callback(resp)})
		}
	}
  
	FaceBook.prototype.loginCallBack = function(response) {
  		var self = this;
	    if (response.status === 'connected') {
	    	self.loggedIn = response;
	    	self.pageScript.login_with_facebook(response.authResponse.userID, response.authResponse.accessToken)
	    } else {
	    	self.pageScript.displayMsg({title:_("Facebook error"),error:_('Can not login with your Facebook account')});
	    } 
	  }

	FaceBook.prototype.fblogin = function() {
		var self = this;
		console.log('fb_login')
		if (! self.loggedIn ) {
			self.getFbUser(self.loginCallBack)
//			FB.login(function(response) {
//				console.log(response)
//			    self.loginCallBack(response);
//			});
		}
	}

	FaceBook.prototype.registerCallBack_ = function(response) {
		var self = this;
	    self.loggedIn = response;
		if (response.status === 'connected') {
			FB.api('/me', function(response2) {
				var email;
		     	if (response2.email) {
		     		email = response2.email;
		     	} else {
		     		e = self.doc.getElementById('RegistrationForm_email_input').value;
		     		if (e != '') {
		     			email = e;
		     		} else {
			     		self.pageScript.displayMsg({ title:"Facebook",message:"please give us an email in the registration form" })
			     		return;
			     	};
		     	};
				self.pageScript.register_with_facebook(response.authResponse.userID, response.authResponse.accessToken, email)
		    });
		} else {
		  self.pageScript.displayMsg({ title:_("Facebook error"), error:'Facebook login is unsuccessful' })
		} 
	}
	
	FaceBook.prototype.registerCallBack = function(response) {
		var self = this;
		if (response.status === 'connected') {
			FB.api('/me', function(response2) {
				document.getElementById("registration-form_identifier_input").value=response.authResponse.userID;
				document.getElementById("registration-form_secret_input").value=response.authResponse.accessToken;
				document.getElementById("registration-form_email_input").value=(response2.email)?response2.email:"Add meg az emailcímed!";
		    });
		} else {
		  self.pageScript.displayMsg({ title:_("Facebook error"), error:_('Can not login with your Facebook account') })
		} 
	}
	
	FaceBook.prototype.fbregister = function() {
		var self = this;
		self.getFbUser(self.registerCallBack);
	}

facebook = new FaceBook(pageScript)
