/*
---------------------------
|	page helper functions |
---------------------------
*/
	
export function deactivate( Id ) {
	if ( element = document.getElementById( Id ) ) {
		deactivate_( element )
	}
	else console.error("deactivate: no element with the given Id")		
}
	
export function deactivate_( element ) {
	if ( typeof element == "object" && element.className) {
		element.className += " inactive";
		saveHandler( element, "onclick" )
	}
	else console.error( "deactivate: element is not an htmlobject" )		
}
	
export function activate( Id, onclickFunc ) {
	if ( element = document.getElementById( Id ) ) {
		activate_( element, onclickFunc )
	}
	else console.error("activate: no element with the given Id")
}
	
export function activate_( element, onclickFunc ) {
	if ( typeof element == "object" ) {
		removeClass( element, "inactive" )
		if ( onclickFunc ) element.onclick = onclickFunc 
		else restoreHandler( element, "onclick" )
	}
	else console.error( "activate: element is not an object" )
}
	
export function removeClass( element, clName ){
	if ( element.className ) element.className=element.className.replace( ' '+clName, "" )
	else console.error( "removeClass: element is not a HTMLobject" )
}

export function saveHandler( element, hName ){
	if ( element && element[hName] ) {
		element.tmp[hname] = element[hName]
		element[hName]=function(){return}
	}
}

export function restoreHandler( element, hName ){
	if ( element && element.tmp[hName] ) {
		element[hname] = element.tmp[hName]
		element.tmp[hName]=function(){return}
	}
}