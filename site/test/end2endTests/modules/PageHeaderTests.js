	var PageHeaderTests = function(assert, testFrame) {
		console.log("this=%o", this)
		var self=this;
		console.log("self=%o", self)
		var done=assert.async();
		var t=testFrame.contentWindow

		self.getPageName = function() {
			var uri = t.document.URL.split("/")
			var lastTag = uri[uri.length -1]
			return lastTag			
		};

		self.assertPageLoaded = function(pageName) {
			console.log("assert")
			return function() {
				console.log("before assert " + pageName)
				assert.equal(self.getPageName(), pageName)
				console.log("after assert" + pageName)
				done();
				console.log("after done" + pageName)
			}
	    };

	    self.testClickingHomeGoesToIndexHtml = function() {
			testFrame.onload=self.assertPageLoaded("index.html")
			t.document.getElementById("nav-bar-home").click()
		};
		
	    self.testClickingHowtoGoesToHowto = function() {
			testFrame.onload=self.assertPageLoaded("user_howto.html")
			t.document.getElementById("nav-bar-howto").click()
		};

	    self.testClickingLoginGoesToLogin = function() {
			testFrame.onload=self.assertPageLoaded("fiokom.html")
			console.log("before")
			t.document.getElementById("nav-bar-login").click()
			console.log("after")
		};
		console.log("self=%o", self)

		return self;
	};

	export default PageHeaderTests;