var QueryString = function () { //http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-url-parameter
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
        // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = pair[1];
        // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]], pair[1] ];
      query_string[pair[0]] = arr;
        // If third or later entry with this name
    } else {
      query_string[pair[0]].push(pair[1]);
    }
  } 
    return query_string;
} ();

function PageScript(debug) {
	var self = this
	this.debug=debug

	PageScript.prototype.ajaxBase = function(callback) {
		var xmlhttp;
		if (window.XMLHttpRequest)
		  {// code for IE7+, Firefox, Chrome, Opera, Safari
		  xmlhttp=new XMLHttpRequest();
		  }
		else
		  {// code for IE6, IE5
		  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		  }
		xmlhttp.onreadystatechange=function()
		  {
		  if (xmlhttp.readyState==4)
		    {
		    	callback(xmlhttp.status,xmlhttp.responseText,xmlhttp.responseXML);
		    }
		  }
		return xmlhttp;
	}

	PageScript.prototype.ajaxpost = function(uri,data,callback) {
		xmlhttp = this.ajaxBase(callback);
		xmlhttp.open("POST",uri,true);
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		l = []
		for (key in data) {
			l.push(key +"=" +encodeURIComponent(data[key]));
		}
		
		xmlhttp.send(l.join("&"));
	}

	PageScript.prototype.ajaxget = function(uri,callback) {
		xmlhttp = this.ajaxBase(callback)
		xmlhttp.open("GET",uri,true);
		xmlhttp.send();
	}

	PageScript.prototype.processErrors = function(data) {
			t = "<ul>"
			if (data.message) {
				document.getElementById("message").innerHTML=data.message
			}
			if (data.assurances) {
				userdata = "email: "+data.email
				userdata +="<br/>userid: "+data.userid
				userdata +="<ul>"
				for(ass in data.assurances) {
					userdata += "<li>"+ass+"</li>"
				}
				userdata +="</ul>"
				document.getElementById("userdata").innerHTML=userdata			
			}
			errs = data.errors
			for ( err in errs ) {
				t += "<li>"+ errs[err] +"</li>"
			}
			t += "</ul>"
			document.getElementById("errorMsg").innerHTML=t
	}

	PageScript.prototype.myCallback = function(status, text) {
		document.getElementById("errorMsg").innerHTML=text
		var data = JSON.parse(text);
		if (status == 200) {
			if(QueryString.next) {
				window.location = decodeURIComponent(QueryString.next)
			}
		}
		self.processErrors(data)
	}

	PageScript.prototype.passwordReset = function() {
	    secret = document.getElementById("PasswordResetForm_secret_input").value;
	    password = document.getElementById("PasswordResetForm_password_input").value;
	    this.ajaxpost("/v1/password_reset", {secret: secret, password: password}, this.myCallback)
	}

	PageScript.prototype.login = function() {
	    username = document.getElementById("LoginForm_username_input").value;
	    username = encodeURIComponent(username)
	    password = document.getElementById("LoginForm_password_input").value;
	    password = encodeURIComponent(password)
	    this.ajaxpost("/login", {credentialType: "password", identifier: username, secret: password}, this.myCallback)
	}

	PageScript.prototype.login_with_facebook = function(userId, accessToken) {
	    username = userId
	    password = encodeURIComponent(accessToken)
	    data = {
	    	credentialType: 'facebook',
	    	identifier: username,
	    	secret: password
	    }
	    this.ajaxpost("/login", data , this.myCallback)
	}

	PageScript.prototype.byEmail = function() {
	    email = document.getElementById("ByEmailForm_email_input").value;
	    email = encodeURIComponent(email)
	    this.ajaxget("/v1/user_by_email/"+email, this.myCallback)
	}

	PageScript.prototype.register = function() {
	    credentialType = document.getElementById("RegistrationForm_credentialType_input").value;
	    identifier = document.getElementById("RegistrationForm_identifier_input").value;
	    secret = document.getElementById("RegistrationForm_secret_input").value;
	    email = document.getElementById("RegistrationForm_email_input").value;
	    digest = document.getElementById("RegistrationForm_digest_input").value;
	    text= {
	    	credentialType: credentialType,
	    	identifier: identifier,
	    	secret: secret,
	    	email: email,
	    	digest: digest
	    }
	    this.ajaxpost("/v1/register", text, this.myCallback)
	}

	PageScript.prototype.register_with_facebook = function(userId, accessToken, email) {
	    username = userId;
	    password = accessToken;
	    text = {
	    	credentialType: "facebook",
	    	identifier: username,
	    	secret: password,
	    	email: email
	    }
	    this.ajaxpost("/v1/register", text, this.myCallback)
	}
	
	PageScript.prototype.getCookie = function(cname) {
	    var name = cname + "=";
	    var ca = document.cookie.split(';');
	    for(var i=0; i<ca.length; i++) {
	        var c = ca[i];
	        while (c.charAt(0)==' ') c = c.substring(1);
	        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
	    }
	    return "";
	} 
	
	PageScript.prototype.addAssurance = function() {
	    digest = document.getElementById("AddAssuranceForm_digest_input").value;
	    assurance = document.getElementById("AddAssuranceForm_assurance_input").value;
	    email = document.getElementById("AddAssuranceForm_email_input").value;
	    csrf_token = this.getCookie('csrf');
	    text= {
	    	digest: digest,
	    	assurance: assurance,
	    	email: email,
	    	csrf_token: csrf_token
	    }
	    this.ajaxpost("/v1/add_assurance", text, this.myCallback)
	}
	
	PageScript.prototype.digestGetter = function(formName) {
		self.formName = formName
		self.idCallback = function(status,text, xml) {
			if (status==200) {
		    	document.getElementById(self.formName + "_digest_input").value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
			} else {
				document.getElementById("errorMsg").innerHTML=text
			}
		}
	
		self.getDigest = function() {
			personalId = document.getElementById(this.formName+"_predigest_input").value;
			text = "<id>"+personalId+"</id>"
			http = this.ajaxBase(this.idCallback);
			http.open("POST",'https://anchor.edemokraciagep.org/anchor',true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
		return self
	}

	PageScript.prototype.loadjs = function(src) {
	    var fileref=document.createElement('script')
	    fileref.setAttribute("type","text/javascript")
	    fileref.setAttribute("src", src)
	    document.getElementsByTagName("head")[0].appendChild(fileref)
	}
	
	PageScript.prototype.unittest = function() {
		this.loadjs("tests.js")
	}
	
	PageScript.prototype.main = function() {
		if (QueryString.secret) {
			document.getElementById("PasswordResetForm_secret_input").value=QueryString.secret
		}
	}

}

pageScript = new PageScript();
