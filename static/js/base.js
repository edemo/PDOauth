function Base(test) {
	var self = this
	test=test || { debug: false, uribase: "" }
	this.debug=test.debug
	win = test.win || window;
    self.pageScript
	this.isLoggedIn=false;
	this.isAssurer=false;
	this.registrationMethode="pw";

	Base.prototype.ajax=function(uri,method,onSuccess,onError){
		console.log(this)
		
	this.prototype.callback = function(next,error){
		var next  = next || function(){return}
		var error = error || defaultErrorHandler
		function callback(status,text,xml) {
			switch (status){
				case 200:
					next(text,xml)
					break;
				case 500:
				case 405:
				case 404:
					this.reportServerFailure(text)
					break;
				default:
					error(status,text,xml)
			}
		}
		function defaultErrorHandler(status,text,xml){
			console.log(text)
			data=JSON.parse(text)
			self.displayMsg(self.processErrors(data))
		}
		return callback
	}

	this.reportServerFailure = function(text){
		self.displayMsg({title:_("Server error occured"),error: text})
	}
	
	this.ajaxBase = function(callback) {
		var xmlhttp;
		if (win.XMLHttpRequest)
		  {// code for IE7+, Firefox, Chrome, Opera, Safari
		  xmlhttp = new win.XMLHttpRequest();
//		  xmlhttp.oName="XMLHttpRequest"; // for testing
		  }
		else
		  {// code for IE6, IE5
		  xmlhttp = new win.ActiveXObject("Microsoft.XMLHTTP");
//		  xmlhttp.oName="ActiveXObject";   // for testing
		  }
		xmlhttp.callback=callback // for testing
		xmlhttp.onreadystatechange=function()
		  {
		  if (xmlhttp.readyState==4)
		    {
		    	callback(xmlhttp.status,xmlhttp.responseText,xmlhttp.responseXML);
		    }
		  }
		return xmlhttp;
	}

	this.ajaxpost = function( uri, data, callback ) {
		xmlhttp = this.ajaxBase( callback );
		xmlhttp.open( "POST", self.uribase + uri, true );
		xmlhttp.setRequestHeader( "Content-type","application/x-www-form-urlencoded" );
		l = []
		for (key in data) l.push( key + "=" + encodeURIComponent( data[key] ) ); 
		var dataString = l.join("&")
		console.log(uri)
		console.log(data)
		xmlhttp.send( dataString );
	}

	this.ajaxget = function( uri, callback, direct) {
		xmlhttp = this.ajaxBase( callback )
		if (direct) {
			theUri = uri;
		} else {
			theUri = self.uribase + uri;
		}
		console.log(theUri)
		xmlhttp.open( "GET", theUri , true);
		xmlhttp.send();
	}
	this.interface = function(){
		if (method=="post") {
			return function(data){
				this.onSuccess=onSuccess
				console.log(this.onSuccess)
				this.onError=onError
				this.ajaxpost(uri,data,this.callback(this.onSuccess,this.onError))
			}
		}
		else {
			a=function(){
				console.log(this.onSuccess)
				this.ajaxget(uri,this.callback(this.onSuccess,this.onError))
			}
			a.onSuccess = onSuccess
			a.onError = onError
			return a
		}	
	}		
	}
}