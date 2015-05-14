
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response.authResponse);
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

  window.fbAsyncInit = function() {
	  FB.init({
	    appId      : '1632759003625536',
	    cookie     : true,  // enable cookies to allow the server to access 
	                        // the session
	    xfbml      : true,  // parse social plugins on this page
	    version    : 'v2.2' // use version 2.2
	  });
	
	  FB.getLoginStatus(function(response) {
	    statusChangeCallback(response);
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

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      console.log('response: ' + DumpObjectIndented(response,' '));
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
  }

  function loginCallBack(response) {
    if (response.status === 'connected') {
    	login_with_facebook(response.authResponse.userID, response.authResponse.accessToken)
    } else {
      document.getElementById('message').innerHTML = 'Facebook login is unsuccessful'
    } 
  }

function fblogin() {
	FB.login(function(response) {
	    loginCallBack(response);
	  });
}

  function registerCallBack(response) {
    if (response.status === 'connected') {
    	register_with_facebook(response.authResponse.userID, response.authResponse.accessToken)
    } else {
      document.getElementById('message').innerHTML = 'Facebook login is unsuccessful'
    } 
  }

function fbregister() {
	FB.login(function(response) {
	    registerCallBack(response);
	  });
}
 