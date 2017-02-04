// module ajax
import { uris } from './adauris';

var uribase = uris.BACKEND_PATH,
	stack = {},			//tacking asyncronous calls
	displayServerResponse = function(response){return response},
	reportServerFailure = function(response){return response},
	win = window        //environment can be mocked
	
export function set_displayServerResponse(func){
	displayServerResponse = func
}

export function set_reportServerFailure(func){
	displayServerResponse = func
}

export function setUribase(theUribase){
	uribase=theUribase
}

export function getStack(){
	return stack;
}

export function callback( next, error ){
		var next  = next || $this.displayServerResponse,
			error = error || $this.displayServerResponse;
		return function( status, response, xml ) {
			switch (status){
				case 200:
					next( response, xml )
					break;
				case 500:
				case 405:
					$this.reportServerFailure( response )
					break;
				default:
					console.log("error ág")
					error( response, xml )
			}
		}
	}
    
export function ajaxBase( callback, uri ) {
		var xmlhttp;
		if (win.XMLHttpRequest) {   // code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp = new win.XMLHttpRequest();
		}
		else {  // code for IE6, IE5
            xmlhttp = new win.ActiveXObject("Microsoft.XMLHTTP");
		}
		xmlhttp.callback=callback   // for testing
		xmlhttp.onreadystatechange=function() {
            if ( xmlhttp.readyState==4 ) {
                stack[uri]="callback"
                callback( xmlhttp.status, xmlhttp.responseText, xmlhttp.responseXML );
                stack[uri]="done"
            }
		}
		return xmlhttp;
	}
    
export function valaidateCallbackArgs( args ){
        var next=null,
            error=null;
        if (typeof args != "undefined") {
            next = args.next || null;
            error = args.error || null
        }
        return { next: next, error: error }
    }
    
export function post( uri, data, callbacks ){
        var cb=$this.valaidateCallbackArgs( callbacks )
        $this.ajaxpost( uri, data, $this.callback( cb.next, cb.error ) )
    }
    
export function ajaxpost( uri, data, callback ) {         //for old style compatibility
		var xmlhttp = $this.ajaxBase( callback, uri ),
			l = []
		xmlhttp.open( "POST", $this.uribase + uri, true );
		xmlhttp.setRequestHeader( "Content-type","application/x-www-form-urlencoded" );
		for (var key in data) l.push( key + "=" + encodeURIComponent( data[key] ) ); 
		xmlhttp.send( l.join("&") );
        $this.stack[uri]="GET"
	}
    
export function get( uri, callbacks, direct){
        var cb=$this.valaidateCallbackArgs( callbacks )
        $this.ajaxget(uri, callback( cb.next, cb.error ), direct || null)
    }
    
export function ajaxget( uri, callback, direct) {       //for old style compatibility
		var xmlhttp = $this.ajaxBase( callback, uri ),
			theUri = direct ? uri : $this.uribase + uri
		xmlhttp.open( "GET", theUri , true);
		xmlhttp.send();
        $this.stack[uri]="GET"
	}
	
export function validateServerMessage(response) {
		if (!response) return {
			errors: [
				"Something went wrong",
				"An empty message is arrived from the server" 
			]
		}
		try { return JSON.parse(response) }
		catch(err) {
			return { 
				errors: [
					"Something went wrong",
					"Unexpected server message:",
                    response
				]
			}
		}
	};
