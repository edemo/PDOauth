// gettext functions
export var _
export var gettext = new (function() {
	var $this={}
	$this.dictionary=[]

	$this.gettext = function() {
		if (!arguments || arguments.length < 1 || !RegExp) return; // called without arguments
		var args=$.map(arguments, function(value, index){return [value]})
        console.log(args)
        if (typeof args[0] != "string") {
                args=args[0]
                var str=args.shift()
                return $this.gettext(str,args.map(function(value, index){return $this.gettext(value)}))
        }
		var str = args.shift();

		if (args.length == 1 && typeof args[0] == 'object') {
			args=args[0].map(function(value, index){return [value]})
		}
	
		// Try to find translated string
		str = $this.dictionary[str] || str

		// Check needed attrubutes given for tokens
		var hasTokens = str.match(/%\D/g),
			hasPhytonTokens = str.match(/{\d}/g)
		if ( (hasTokens && hasTokens.length != args.length) || (hasPhytonTokens && hasPhytonTokens.length != args.length)) {
			console.log('Gettext error: Arguments count ('+ args.length +') does not match replacement token count ('+ ((hasTokens && hasTokens.length) + (hasPhytonTokens && hasPhytonTokens.length)) + ').');
			return str;
		}
		
		if (hasTokens) {
			// replace tokens with the given arguments
			var re  = /([^%]*)%('.|0|\x20)?(-)?(\d+)?(\.\d+)?(%|b|c|d|u|f|o|s|x|X)(.*)/; //'
			var a = [], b = [], i = 0, numMatches = 0;		
			while (a = re.exec(str)) {
				var leftpart   = a[1], 
					pPad  = a[2], 
					pJustify  = a[3], 
					pMinLength = a[4],
					pPrecision = a[5], 
					pType = a[6], 
					rightPart = a[7];
				numMatches++;
				if (pType == '%') subst = '%';
				else {
					var param = args[i],
						pad   = '',
						justifyRight = true,
						minLength = -1,
						precision = -1,
						subst = param;
					if (pPad && pPad.substr(0,1) == "'") pad = leftpart.substr(1,1);
					else if (pPad) pad = pPad;
					if (pJustify && pJustify === "-") justifyRight = false;
					if (pMinLength) minLength = parseInt(pMinLength);
					if (pPrecision && pType == 'f') precision = parseInt(pPrecision.substring(1));
					if (pType == 'b')      subst = parseInt(param).toString(2);
					else if (pType == 'c') subst = String.fromCharCode(parseInt(param));
					else if (pType == 'd') subst = parseInt(param) ? parseInt(param) : 0;
					else if (pType == 'u') subst = Math.abs(param);
					else if (pType == 'f') subst = (precision > -1) ? Math.round(parseFloat(param) * Math.pow(10, precision)) / Math.pow(10, precision): parseFloat(param);
					else if (pType == 'o') subst = parseInt(param).toString(8);
					else if (pType == 's') subst = param;
					else if (pType == 'x') subst = ('' + parseInt(param).toString(16)).toLowerCase();
					else if (pType == 'X') subst = ('' + parseInt(param).toString(16)).toUpperCase();
				}
				str = leftpart + subst + rightPart;
				i++;
			}
		}
		if (hasPhytonTokens){
			args.forEach( function(value,key){ str=str.replace("{"+key+"}",value)} )
		}
		return str;
	}
	
	$this.initGettext = function(text) {
		// waiting for gettext loads po files
		try {
			$this.dictionary=JSON.parse(text)
			_=function() { return $this.gettext.apply( this, arguments ) } 
		}
		catch (e) {
			$this.mockGettext()
		}
		window.traces.push("init gettext")
	}
	
	$this.mockGettext = function(){
		_= function(str) { return str }
	}
	
	return $this
})()

