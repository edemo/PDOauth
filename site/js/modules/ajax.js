
export default function(args){
 
    var $this = {},
        win = args.environment || window  //window can be mocked
     
    $this.stack = {}
    
    $this.uribase = args.uribase || ''
    
    $this.displayServerResponse = args.displayServerResponse || function(response){return response}
    
    $this.reportServerFailure = args.reportServerFailure || function(response){return repsonse}

    $this.callback = function( next, error ){
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
					error( response, xml )
			}
		}
	}
    
    $this.ajaxBase= function( callback, uri ) {
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
                $this.stack[uri]="callback"
                callback( xmlhttp.status, xmlhttp.responseText, xmlhttp.responseXML );
                $this.stack[uri]="done"
            }
		}
		return xmlhttp;
	}

    
    $this.valaidateCallbackArgs(arg){
        var next=null,
            error=null;
        if (typeof arg != "undefined") {
            next = arg.next || null;
            error = arg.error || null
        }
        return {next: next, error: error }
    }
    
    $this.post=function( uri, data, callbacks ){
        var cb=$this.valaidateCallbackArgs( callbacks )
        $this.ajaxpost( uri, data, $this.callback( cb.next, cb.error ) )
    }
    
    $this.ajaxpost= function( uri, data, callbacks ) {         //for old style compatibility
		xmlhttp = $this.ajaxBase( callback, uri );
		xmlhttp.open( "POST", self.uribase + uri, true );
		xmlhttp.setRequestHeader( "Content-type","application/x-www-form-urlencoded" );
		l = []
		for (key in data) l.push( key + "=" + encodeURIComponent( data[key] ) ); 
		var dataString = l.join("&")
		xmlhttp.send( dataString );
        $this.stack[uri]="GET"
	}
    
    $this.get=function(uri, callbacks, direct){
        var cb=$this.valaidateCallbackArgs(callbacks)
        $this.ajaxget(uri, $this.callback(cb.next,cb.error), direct || null)
    }
    
	$this.ajaxget= function( uri, callback, direct) {       //for old style compatibility
		xmlhttp = this.ajaxBase( callback, uri )
		if (direct) {
			theUri = uri;
		} else {
			theUri = $rhis.uribase + uri;
		}
		xmlhttp.open( "GET", theUri , true);
		xmlhttp.send();
        $this.stack[uri]="GET"
	}
	
    $this.validateServerMessage= function (response) {
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
	}
    
    return $this
}
