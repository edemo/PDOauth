/*
-------------------------
|  messaging functions	|
-------------------------
*/
import * as Control from './control'

var target,
	displayInPopup = function( msg ) {
		if (!(msg.title || msg.error || msg.message || msg.success)) return
		$("#myModal").modal();
		var close = function(){ closePopup( msg.callback || null ) }
		Control.activate( "PopupWindow_CloseButton1", close )
		Control.activate( "PopupWindow_CloseButton2", close )
		Control.innerHTML( "PopupWindow_TitleDiv", msg.title || "" )
		Control.innerHTML( "PopupWindow_ErrorDiv", msg.error || "" )
		Control.innerHTML( "PopupWindow_MessageDiv", msg.message || "" )
		Control.innerHTML( "PopupWindow_SuccessDiv", msg.success || "" )
		window.traces.push ("MSGbox ready" )
	},
	displayInDiv = function( msg ) {
		var text=(msg.error)?msg.error:""+(msg.success)?msg.success:""
		Control.innerHTML("message-container", text)
		Control.show("message-container")
	}

export function setTarget( theTarget ){
	target=theTarget
}

export function display( msg ) {
	switch ( target ) {
		case "popup":
			displayInPopup (msg );
			break;
		case "div":
			displayInDiv( msg );
			break;
	} 
}

export function closePopup(popupCallback) {
	Control.innerHTML("PopupWindow_TitleDiv","")
	Control.innerHTML("PopupWindow_ErrorDiv","")
	Control.innerHTML("PopupWindow_MessageDiv","")
	Control.innerHTML("PopupWindow_SuccessDiv","")
	if ( popupCallback ) popupCallback();
	window.traces.push("popup closed")
	return "closePopup";
}