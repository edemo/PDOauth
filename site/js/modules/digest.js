/*
-----------------------------
|  digest getter functions	|
-----------------------------
*/

import { _ } from './gettext'
import { uris } from './adauris'
import * as Control from './control'
import * as Ajax from './ajax'
import * as Msg from './messaging'
 
export function digestGetter(formName) {
	var $this={}
	var formName=formName,
	digestCallback = function(status,text,xml) {
		if (status==200) {
			window.traces.push("digest cb")
			Control.setValue( formName + "_digest_input", xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue );
			$("#"+formName + "_digest-input").trigger('keyup');
			Control.setValue( formName + "_predigest_input", "" )
			switch (formName) {
				case "assurancing":
					var messageBox=document.getElementById("assurance-giving_message")
					messageBox.innerHTML=_("The Secret Hash is given for assuring")
					messageBox.className="given"
					Control.activate("assurance-giving_submit-button")
					break;
				case "login":
				case "change-hash-form":
					self.changeHash()
					break;
				case "registration-form":
					Control.hide( formName + "_code-generation-input")
					Control.hide( formName + "_digest_input" )
					Control.activate( formName + "_make-here", function(){$this.digestGetter(formName).methodChooser('here')} )
					break;
				default:
					Control.hide( formName + "_code-generation-input")
			}
			window.traces.push("gotDigest")
		}
		else {
			Msg.display({title:_("Error message"),error: text});
			diegestInput.value =""
			if (formName=="assurancing") {
				var messageBox=document.getElementById("assurance-giving_message")
				messageBox.innerHTML=_("The Secret Hash isn't given yet")
				messageBox.className="missing"
				Control.deactivate("assurance-giving_submit-button")
			}
		}
	},
	createXmlForAnchor = function(formName) {
		console.log(formName)
		var personalId = normalizeId( Control.getValue( formName + "_predigest_input" ) ),
			mothername = normalizeString( Control.getValue( formName + "_predigest_mothername" ) );
		if ( personalId == "") {
			Msg.display({title:_('Missing data'), error:_("Personal identifier is missing")})
			return;
		}
		if ( mothername == "") {
			Msg.display({title:_('Missing data'), error:_("Mother's name is missing")})
			return;
		}
		return ("<request><id>"+personalId+"</id><mothername>"+mothername+"</mothername></request>");
	},
	buttonFunc = function ( method ){
		return function(){ $this.digestGetter( formName ).methodChooser( method ) }
	} 
		
	$this.methodChooser = function( method ) {
		var selfButton = formName+"_make-self",
			hereButton = formName+"_make-here";
		switch (method) {
			case "here":
				Control.show( formName + "_code-generation-input" )
				Control.hide( formName + "_digest-input" )
				Control.activate( selfButton, buttonFunc('self') )
				Control.deactivate( hereButton )
				break;
			case "self":
				Control.hide( formName+"_code-generation-input" )
				Control.show( formName+"_digest-input" )
				Control.activate( hereButton, buttonfunc('here') )
				Control.deactivate( selfButton )
				break;
			default:
		}
	}
		
	$this.getDigest = function() {
		var text = createXmlForAnchor(formName)
		if (text == null) return;
		var http = Ajax.base( digestCallback );
		http.open( "POST", uris.ANCHOR_URL + "anchor", true );
		http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		http.setRequestHeader("Content-length", text.length);
		http.setRequestHeader("Connection", "close");
		http.send(text);
	}
	
	return $this
}
	
export function normalizeString( val ) {
	var   accented = "ˆ¸Ûı˙È·˚Ì÷‹”’⁄…¡€Õ",
		unaccented = "ouooueauiouooueaui",
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

export function normalizeId(val) {
	return val.replace(/[^0-9]/g,"");
}
	
export function refreshMonitor( formName ) {
	var motherName = normalizeString( Control.getValue( formName + "_mothername") ),
		id = normalizeId( Control.getValue( formName+"_input" ) );
	Control.innerHTML( formName + "_monitor", id + ' - ' + motherName );
}