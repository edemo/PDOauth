function TFRWRK(test) {

	var self = this,
		test=test || { debug: false },
		win = test.win || window;

	TFRWRK.prototype.callback = function(next,error){
		var next  = next || function(){return},
			error = error || function(status,text,xml){
				console.error(status)
			},
			callback = function(status,text,xml) {
				console.log(status)
				switch (status){
					case 200:
						next(text,xml)
						break;
					default:
						error(status,text,xml)
				}
			}
		return callback;
	}
	
	TFRWRK.prototype.ajaxBase = function(callback) {
		var xmlhttp;
		if (win.XMLHttpRequest) {
			// code for IE7+, Firefox, Chrome, Opera, Safari
			xmlhttp = new win.XMLHttpRequest();
		}
		else {
			// code for IE6, IE5
			xmlhttp = new win.ActiveXObject("Microsoft.XMLHTTP");
		}
		xmlhttp.callback=callback // for testing
		xmlhttp.onreadystatechange=function() {
			if (xmlhttp.readyState==4)  {
		    	callback(xmlhttp.status,xmlhttp.responseText,xmlhttp.responseXML);
		    }
		}
		return xmlhttp;
	}

	TFRWRK.prototype.ajaxpost = function( uri, data, callback ) {
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

	TFRWRK.prototype.ajaxget = function( uri, callback) {
		var xmlhttp = this.ajaxBase( callback )
		console.log(uri)
		xmlhttp.open( "GET", uri , true);
		xmlhttp.send();
	}

	TFRWRK.prototype.loadPage = function(page, testScript){
		console.log("loadpage")
		var testFrame=document.getElementById('testarea')
		testFrame.onload=function(){
				testScript(testFrame);
				}
		testFrame.src='../'+page
	}
	
	TFRWRK.prototype.loadTest = function(test){
		var loadTestCallback = function(js){
			console.log("loadtestcallback")
			sessionStorage.clear();
			document.getElementById("qunit").innerHTML=""
			QUnit.init()
			QUnit.load()
			eval(js);
		}
		self.ajaxget(test+".js", self.callback(loadTestCallback))
	}	
	
	TFRWRK.prototype.doTest = function(url, test) {
		var loadMockCallback = function(mock){
			var loadUtestCallback = function(uTest){
				var tFrame=document.getElementById('testarea')
				tFrame.onload=function(){
					var tWin=tFrame.contentWindow,
						sContainer=tWin.document.createElement('script')
					tWin.QUnit=QUnit
					tWin.console=console
					sContainer.setAttribute("type","text/javascript");
					sContainer.innerHTML=mock+uTest;
					QUnit.XmlContainer = document.getElementById("qunit-xml")
					tWin.document.getElementsByTagName("body")[0].appendChild(sContainer);
				}
				tFrame.src='../'+url
			}
			self.ajaxget("unitTests/"+test+".tst.js", self.callback(loadUtestCallback))
		}
		self.ajaxget("unitTests/_mock.js", self.callback(loadMockCallback))		
	}
	
}
	
tfrwrk = new TFRWRK();
