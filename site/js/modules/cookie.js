export function	set = function( cname, cvalue, expireDays, path ) {
	var date = new Date(),	
		expireDays = expireDays || 1,
		path = path || '/'
	date.setTime(date.getTime() + (expireDays*24*60*60*1000));
	var expires = "expires="+ date.toUTCString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=" + path;
} 

export function get = function(cname) {
	var name = cname + "=";
	var ca = win.document.cookie.split(';');
	for ( var i=0; i<ca.length; i++ ) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1);
		if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
	}
	return false;
} 