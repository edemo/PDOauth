/*
-----------------------------
|  digest getter functions	|
-----------------------------
*/

//Getdigest functions
	
	PageScript.prototype.normalizeString = function(val) {
		var   accented="öüóõúéáûíÖÜÓÕÚÉÁÛÍ",
			unaccented="ouooueauiouooueaui",
			s = "",
			c;
		
		for (var i = 0, len = val.length; i < len; i++) {
		  c = val[i];
		  if(c.match('[abcdefghijklmnopqrstuvwxyz]')) {
		    s=s+c;
		  } else if(c.match('[ABCDEFGHIJKLMNOPQRSTUVXYZ]')) {
		    s=s+c.toLowerCase();
		  } else if(c.match('['+accented+']')) {
		    for (var j = 0, alen = accented.length; j <alen; j++) {
		      if(c.match(accented[j])) {
		        s=s+unaccented[j];
		      }
		    }
		  }
		}
		return s;
	}
	
	// removing all non numeric characters
	PageScript.prototype.normalizeId = function(val) {
		return val.replace(/[^0-9]/g,"");
	}
	
	PageScript.prototype.digestGetter = function(formName) {
		var formName=formName,
		digestCallback = function(status,text,xml) {
			var diegestInput=document.getElementById(formName + "_digest_input")
			if (status==200) {
				window.traces.push("digest cb")
				diegestInput.value = xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue;
				console.log(diegestInput.value)
				$("#"+formName + "_digest-input").trigger('keyup');
				document.getElementById(formName + "_predigest_input").value = "";
				switch (formName) {
					case "assurancing":
						var messageBox=document.getElementById("assurance-giving_message")
						messageBox.innerHTML=_("The Secret Hash is given for assuring")
						messageBox.className="given"
						document.getElementById("assurance-giving_submit-button").className=""
						break;
					case "login":
					case "change-hash-form":
						self.changeHash()
						break;
					case "registration-form":
						console.log("formname is " + formName)
						var style = document.getElementById(formName+"_code-generation-input").style;
						console.log("style:" + formName)
						style.display="none"
						document.getElementById(formName+"_digest_input").style.display="block"
						Control.activate( formName+"_make-here", function(){self.digestGetter(formName).methodChooser('here')})
						break;
					default:
						style.display="none"
				}
				window.traces.push("gotDigest")
			}
			else {
				self.displayMsg({title:_("Error message"),error: text});
				diegestInput.value =""
				if (formName=="assurancing") {
					var messageBox=document.getElementById("assurance-giving_message")
					messageBox.innerHTML=_("The Secret Hash isn't given yet")
					messageBox.className="missing"
					document.getElementById("assurance-giving_submit-button").className="inactive"
				}
			}
		}

		this.methodChooser = function(method) {
			var selfButton = formName+"_make-self"
			var hereButton = formName+"_make-here"
			switch (method) {
				case "here":
					document.getElementById(formName+"_code-generation-input").style.display="block"
					document.getElementById(formName+"_digest-input").style.display="none"
					Control.activate( selfButton, function(){self.digestGetter(formName).methodChooser('self')} )
					Control.deactivate( hereButton )
					break;
				case "self":
					document.getElementById(formName+"_code-generation-input").style.display="none"
					document.getElementById(formName+"_digest-input").style.display="block"
					Control.activate( hereButton, function(){self.digestGetter(formName).methodChooser('here')} )
					Control.deactivate( selfButton )
					break;
				default:
			}
		}
		
		this.getDigest = function() {
			var text = createXmlForAnchor(formName)
			if (text == null) return;
			var http = self.ajaxBase(digestCallback);
			http.open("POST",self.QueryString.uris.ANCHOR_URL+"anchor",true);
			http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		  	http.setRequestHeader("Content-length", text.length);
		  	http.setRequestHeader("Connection", "close");
			http.send(text);
		}
	
		function createXmlForAnchor(formName) {
			console.log(formName)
			var personalId = selrmalizeId(document.getElementById(formName+"_predigest_input").value),
				motherValue = document.getElementById(formName+"_predigest_mothername").value,
				mothername = self.normalizeString(motherValue);
			if ( personalId == "") {
				self.displayMsg({title:_('Missing data'), error:_("Personal identifier is missing")})
				return;
			}
			if ( mothername == "") {
				self.displayMsg({title:_('Missing data'), error:_("Mother's name is missing")})
				return;
			}
			return ("<request><id>"+personalId+"</id><mothername>"+mothername+"</mothername></request>");
		}
		
		return this
	}
	
	PageScript.prototype.convert_mothername = function(formName) {
		var inputElement = document.getElementById( formName+"_mothername");
		var outputElement = document.getElementById( formName+"_monitor");
		outputElement.innerHTML = self.normalizeId(document.getElementById( formName+"_input").value) +' - '+ self.normalizeString(inputElement.value);
	}