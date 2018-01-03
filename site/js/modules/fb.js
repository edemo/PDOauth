import { _ } from './gettext'
import * as Control from './control'

var FaceBook = function(pageScript) {
	var $this=this
	$this.pageScript = pageScript;
	$this.doc = document;
	$this.loggedIn = false;
	window.traces.push("fb constructor")

	
	FaceBook.prototype.getMeCallback = function(response){
		if (response.email) document.getElementById("registration-form_email_input").value=response.email;
		else document.getElementById("registration-form_email_input").placeholder=_("Type here your email address");
		window.traces.push("getMecallback")		
	}
	
	FaceBook.prototype.registerCallBack = function(response) {
		window.traces.push("registerCallBack begin")
		if (response.status == 'connected' && response.authResponse.userID && response.authResponse.userID!="" && response.authResponse.accessToken && response.authResponse.accessToken!="" ) {
			document.getElementById("registration-form_email_input").value=response.authResponse.userID;
			document.getElementById("registration-form_secret_input").value=response.authResponse.accessToken;
			FB.api('/me?fields=email', {fields:"email"}, function(r){ $this.getMeCallback(r)} );
		} else {
		  Msg.message({ title:_("Facebook error"), error:_("Connection to facebook was unsuccesfull") })
		} 
		window.traces.push("registerCallBack end")
	}

  	FaceBook.prototype.fbinit = function() {
		var appID
		if (appID=$this.pageScript.QueryString.uris.FACEBOOK_APP_ID) {
			window.fbAsyncInit = function() {
				FB.init({
					appId	: appID,
					cookie	: true,  // enable cookies to allow the server to access 
								// the session
					xfbml	: true,  // parse social plugins on this page
					status	: true,
					version	: 'v2.3' // use version 2.2
				});
				$this.pageScript.isFBsdkLoaded=true
				Control.activate("Facebook_login_button", facebook.fblogin)
				Control.activate("registration-form-method-selector-fb", function(){pageScript.setRegistrationMethode('fb')})
				window.traces.push("fbAsyncInit")
			};

  // Load the SDK asynchronously
			(function(d, s, id) {
				var js, fjs = d.getElementsByTagName(s)[0];
				if (d.getElementById(id)) return;
				js = d.createElement(s); js.id = id;
				js.src = "//connect.facebook.net/en_US/sdk.js";
				fjs.parentNode.insertBefore(js, fjs);
			}(document, 'script', 'facebook-jssdk'));
		}
		window.traces.push("fbinit")
	}
  
	FaceBook.prototype.credentialCallBack = function(response) {
	    if (response.status === 'connected') {
	    	$this.loggedIn = response;
	    	$this.pageScript.add_facebook_credential(response.authResponse.userID, response.authResponse.accessToken)
	    } else {
	    	$this.doc.getElementById('AddCredentialForm_ErrorMsg').innerHTML = '<p class="warning">A facebook bejelentkezés sikertelen</p>';
	    } 
	  }

	FaceBook.prototype.add_fb_credential = function() {
		if (! $this.loggedIn ) {
//			FB.login(function(response) {
//			    $this.credentialCallBack(response);
			$this.getFbUser($this.credentialCallBack)
		};
	}
	
	FaceBook.prototype.getFbUser  =function(callback) {
		FB.getLoginStatus( function(resp){$this.statusChangeCallback(resp,callback)})
	}
	
	FaceBook.prototype.statusChangeCallback = function(response,callback) {
		if (response.status === 'connected') {
			callback(response)
		} else if (response.status === 'not_authorized') {
			FB.login(function(resp){callback(resp)},{scope: 'email'})
		} else {
			FB.login(function(resp){callback(resp)},{scope: 'email'})
		}
	}
  
	FaceBook.prototype.loginCallBack = function(response) {
	    if (response.status === 'connected' && response.authResponse.userID && response.authResponse.userID!="" && response.authResponse.accessToken && response.authResponse.accessToken!="") {
	    	$this.loggedIn = response;
	    	$this.pageScript.login( 'facebook', response.authResponse.userID, response.authResponse.accessToken)
	    } else {
	    	Msg.display({title:_("Facebook error"),error:_('Can not login with your Facebook account')});
	    } 
	  }

	FaceBook.prototype.fblogin = function() {
		if (! $this.loggedIn ) {
			$this.getFbUser($this.loginCallBack)
//			FB.login(function(response) {
//			    $this.loginCallBack(response);
//			});
		}
	}

	FaceBook.prototype.registerCallBack_ = function(response) {
	    $this.loggedIn = response;
		if (response.status === 'connected') {
			FB.api('/me?fields=email', function(response2) {
				var email;
		     	if (response2.email) {
		     		email = response2.email;
		     	} else {
		     		e = $this.doc.getElementById('RegistrationForm_email_input').value;
		     		if (e != '') {
		     			email = e;
		     		} else {
			     		Msg.display({ title:"Facebook",message:"please give us an email in the registration form" })
			     		return;
			     	};
		     	};
				$this.pageScript.register_with_facebook(response.authResponse.userID, response.authResponse.accessToken, email)
		    });
		} else {
		  Msg.display({ title:_("Facebook error"), error:'Facebook login is unsuccessful' })
		} 
	}

	FaceBook.prototype.fbregister = function() {
		$this.getFbUser($this.registerCallBack);
		window.traces.push("fbRegister")
	}
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
    FB.api('/me?fields=email', function(response) {
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
  }
	
export default FaceBook
