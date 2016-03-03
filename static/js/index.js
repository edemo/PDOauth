PageScript.prototype.page = "index";

PageScript.prototype.main = function() {
	this.ajaxget("/adauris", this.uriCallback)
	console.log('index')
}

	