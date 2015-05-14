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

function ajaxBase(callback) {
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

function ajaxpost(uri,data,callback)
{
	xmlhttp = ajaxBase(callback);
	xmlhttp.open("POST",uri,true);
	xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	xmlhttp.send(data);
}

function ajaxget(uri,callback)
{
	xmlhttp = ajaxBase(callback)
	xmlhttp.open("GET",uri,true);
	xmlhttp.send();
}

function processErrors(data) {
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

function myCallback(status, text) {
	document.getElementById("errorMsg").innerHTML=text
	var data = JSON.parse(text);
	if (status == 200) {
		if(QueryString.next) {
			window.location = QueryString.next
		}
	}
	processErrors(data)
}

function passwordReset() {
    secret = document.getElementById("PasswordResetForm_secret_input").value;
    password = document.getElementById("PasswordResetForm_password_input").value;
    ajaxpost("/v1/password_reset", "secret="+secret+"&password="+password, myCallback)
}

function login() {
    username = document.getElementById("LoginForm_username_input").value;
    password = document.getElementById("LoginForm_password_input").value;
    ajaxpost("/login", "credentialType=password&username="+username+"&password="+password, myCallback)
}

function login_with_facebook(userId, accessToken) {
    username = userId;
    password = accessToken;
    ajaxpost("/login", "credentialType=facebook&username="+username+"&password="+password, myCallback)
}

function byEmail() {
    email = document.getElementById("ByEmailForm_email_input").value;
    ajaxget("/v1/user_by_email/"+email, myCallback)
}

function register() {
    credentialType = document.getElementById("RegistrationForm_credentialType_input").value;
    identifier = document.getElementById("RegistrationForm_identifier_input").value;
    secret = document.getElementById("RegistrationForm_secret_input").value;
    email = document.getElementById("RegistrationForm_email_input").value;
    digest = document.getElementById("RegistrationForm_digest_input").value;
    text= 
    	"credentialType=" + credentialType +
    	"&identifier=" + identifier +
    	"&secret=" + secret +
    	"&email=" + email +
    	"&digest=" + digest;
    ajaxpost("/v1/register", text, myCallback)
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
} 

function addAssurance() {
    digest = document.getElementById("AddAssuranceForm_digest_input").value;
    assurance = document.getElementById("AddAssuranceForm_assurance_input").value;
    email = document.getElementById("AddAssuranceForm_email_input").value;
    csrf_token = getCookie('csrf');
    console.log("csrf_tokenn:"+csrf_token)
    text= 
    	"digest=" + digest +
    	"&assurance=" + assurance +
    	"&email=" + email +
    	"&csrf_token=" + csrf_token;
    ajaxpost("/v1/add_assurance", text, myCallback)
}

function DigestGetter(formName) {
	var self = this
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
		http = ajaxBase(idCallback);
		http.open("POST",'https://anchor.edemokraciagep.org/anchor',true);
		http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	  	http.setRequestHeader("Content-length", text.length);
	  	http.setRequestHeader("Connection", "close");
		http.send(text);
	}
	return self
}

function main() {
	if (QueryString.secret) {
		document.getElementById("PasswordResetForm_secret_input").value=QueryString.secret
	}
}
