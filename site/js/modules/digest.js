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
 
export function getter( formName, callback ) {
	var $this={},
	createXmlForAnchor = function(formName) {
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
		return function(){ getter( $this.formName ).methodChooser( method ) }
	} 
	$this.formName=formName
	$this.digestCallback = function(status,text,xml) {
		if (status==200) {
			window.traces.push("digest cb")
			Control.setValue( $this.formName + "_digest_input", xml.getElementsByTagName('hash')[0].childNodes[0].nodeValue );
			$("#"+$this.formName + "_digest-input").trigger('keyup');
			Control.setValue( $this.formName + "_predigest_input", "" )
			switch ($this.formName) {
				case "assurancing":
					var messageBox=document.getElementById("assurance-giving_message")
					messageBox.innerHTML=_("The Secret Hash is given for assuring")
					messageBox.className="given"
					Control.activate("assurance-giving_submit-button")
					break;
				case "login":
				case "change-hash-form":
					callback()
					break;
				case "registration-form":
					Control.hide( $this.formName + "_code-generation-input")
					Control.hide( $this.formName + "_digest_input" )
					Control.activate( $this.formName + "_make-here", function(){getter($this.formName).methodChooser('here')} )
					break;
				default:
					Control.hide( $this.formName + "_code-generation-input")
			}
			window.traces.push("gotDigest")
		}
		else {
			var message = (status==0) ? _("The anchor server is not responding") : text
			Msg.display( { title:_("Error message"), error: message } );
			Control.setValue( $this.formName + "_digest_input", "" )
			if ( $this.formName=="assurancing" ) {
				var messageBox=document.getElementById("assurance-giving_message")
				messageBox.innerHTML=_("The Secret Hash isn't given yet")
				messageBox.className="missing"
				Control.deactivate("assurance-giving_submit-button")
			}
		}
	}		
	$this.methodChooser = function( method ) {
		var selfButton = $this.formName+"_make-self",
			hereButton = $this.formName+"_make-here";
		switch (method) {
			case "here":
				Control.show( $this.formName + "_code-generation-input" )
				Control.hide( $this.formName + "_digest-input" )
				Control.activate( selfButton, buttonFunc('self') )
				Control.deactivate( hereButton )
				break;
			case "self":
				Control.hide( $this.formName+"_code-generation-input" )
				Control.show( $this.formName+"_digest-input" )
				Control.activate( hereButton, buttonfunc('here') )
				Control.deactivate( selfButton )
				break;
			default:
		}
	}
		
	$this.getDigest = function() {
		var text = createXmlForAnchor($this.formName)
		if (text == null) return;
		var http = Ajax.base( $this.digestCallback );
		http.open( "POST", uris.ANCHOR_URL + "anchor", true );
		http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		http.setRequestHeader("Content-length", text.length);
		http.setRequestHeader("Connection", "close");
		http.send(text);
	}
	
	return $this
}
	
export function normalizeString( val ) {
	var   accented = "öüóőúéáűíÖÜÓŐÚÉÁŰÍ",
		unaccented = "ouooueauiouooueaui",
		s = "",
		c;
	
	for (var i = 0, len = val.length; i < len; i++) {
	  c = val[i];
	  if(c.match('[abcdefghijklmnopqrstuvwxyz]')) {
		s=s+c;
	  } else if(c.match('[ABCDEFGHIJKLMNOPQRSTUVXYZ]')) {
		s=s+c.toLowerCase();
	  } else if(c.match(/[öüóőúéáűíÖÜÓŐÚÉÁŰÍ]/g)) {
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