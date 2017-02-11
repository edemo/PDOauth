var Ajax = function( args ){
 
    var $this = {},
        win = args.environment || window  //window can be mocked
     
    $this.stack = {}
    
    $this.uribase = ''
    
    $this.displayServerResponse = function(response){return response}
    
    $this.reportServerFailure = function(response){return response}

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
					console.log("error ág")
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

    
    $this.valaidateCallbackArgs=function(args){
        var next=null,
            error=null;
        if (typeof args != "undefined") {
            next = args.next || null;
            error = args.error || null
        }
        return {next: next, error: error }
    }
    
    $this.post=function( uri, data, callbacks ){
        var cb=$this.valaidateCallbackArgs( callbacks )
        $this.ajaxpost( uri, data, $this.callback( cb.next, cb.error ) )
    }
    
    $this.ajaxpost= function( uri, data, callback ) {         //for old style compatibility
		var xmlhttp = $this.ajaxBase( callback, uri ),
			l = []
		xmlhttp.open( "POST", $this.uribase + uri, true );
		xmlhttp.setRequestHeader( "Content-type","application/x-www-form-urlencoded" );
		for (var key in data) l.push( key + "=" + encodeURIComponent( data[key] ) ); 
		xmlhttp.send( l.join("&") );
        $this.stack[uri]="GET"
	}
    
    $this.get=function(uri, callbacks, direct){
        var cb=$this.valaidateCallbackArgs(callbacks)
        $this.ajaxget(uri, $this.callback(cb.next,cb.error), direct || null)
    }
    
    $this.ajaxget= function( uri, callback, direct) {       //for old style compatibility
		var xmlhttp = $this.ajaxBase( callback, uri ),
			theUri = direct ? uri : $this.uribase + uri
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
export default Ajax;
