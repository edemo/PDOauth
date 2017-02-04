/*
---------------------------
|	page helper functions |
---------------------------
*/
	
export function deactivateControl( Id ) {
	if ( control = document.getElementById( Id ) ) {
		deactivateControl_( control )
	}
	else console.error("deactivateControl: no element with the given Id")		
}
	
export function deactivateControl_( control ) {
	if ( control = document.getElementById( Id ) && control.className) {
		control.className += " inactive";
		saveHandler( control, "onclick" )
	}
	else console.error( "deactivateControl: control is not an htmlobject" )		
}
	
export function activateControl( Id, onclickFunc ) {
	if ( control = document.getElementById( Id ) ) {
		activateControl_( control, onclickFunc )
	}
	else console.error("activateControl: no element with the given Id")
}
	
export function activateControl_( control, onclickFunc ) {
	if ( typeof control == "object" ) {
		removeClass( control, "inactive" )
		if ( onclickFunc ) control.onclick = onclickFunc 
		else restoreHandler( control, "onclick" )
	}
	else console.error( "activateControl: control is not an object" )
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