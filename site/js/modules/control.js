/*
---------------------------
|	page helper functions |
---------------------------
*/
	
export function deactivate( Id ) {
	var element = document.getElementById( Id )
	if ( element ) deactivate_( element )
	else console.error( "deactivate: no element with the given Id" )		
}
	
export function deactivate_( element ) {
	if ( typeof element == "object" && element.className) {
		element.className += " inactive";
		saveHandler( element, "onclick" )
	}
	else console.error( "deactivate: element is not an htmlobject" )		
}
	
export function activate( Id, onclickFunc ) {
	var element = document.getElementById( Id )
	if ( element ) activate_( element, onclickFunc )
	else console.error( "activate: no element with the given Id" )
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

export function hide( Id ) {
	var element = document.getElementById( Id )
	if ( element ) hide_( element )
	else console.error( "hide: no element with the given Id" )
}

export function hide_( element ) {
	if ( typeof element == "object" && typeof element.style != "undefined") element.style.display = "none"
	else console.error( "hide: element is not an HTMLobject" )
}

export function show( Id ) {
	var element = document.getElementById( Id )
	if ( element ) hide_( element )
	else console.error( "show: no element with the given Id" )
}
	
export function show_( element ) {
	if ( typeof element == "object" && typeof element.style != "undefined") element.style.display = "block"
	else console.error( "show: element is not an HTMLobject" )
}

export function getValue( Id ) {
	var element = document.getElementById( Id )
	if ( element ) return getValue_( element )
	else console.error( "getValue: no element with the given Id" )
}
	
export function getValue_( element ) {
	if ( typeof element == "object") return element.value
	else {
		console.error( "getValue: element is not a HTMLobject" )
		return null;
	}
}

export function setValue( Id, data ) {
	var element = document.getElementById( Id )
	if ( element ) setValue_( element, data )
	else console.error( "setValue: no element with the given Id" )
}
	
export function setValue_( element, data ) {
	if ( typeof element == "object" ) element.value = data
	else console.error( "setValue: element is not a HTMLobject" )

}

export function innerHTML( Id, HTML ) {
	var element = document.getElementById( Id )
	if ( element ) innerHTML_( element, HTML )
	else console.error( "innerHTML: no element with the given Id" )
}
	
export function innerHTML_( element, HTML ) {
	if ( typeof element == "object" ) element.innerHTML = HTML
	else console.error( "innerHTML: element is not a HTMLobject" )
}