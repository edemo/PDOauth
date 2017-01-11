account_uTest = function(testFrame){
var t
if ( (testFrame) && (t=testFrame.contentWindow) ) {}
else return

t.QUnit=QUnit
t.console=console
var qunitXmlContainer = document.getElementById("qunit-xml").innerHTML

var testCollection=function() {

var test=
	{
		win: {
//			XMLHttpRequest: testXMLHttpRequestObject,
			location: window.location
			},
		debug: true,
		uribase: "/ada"
	}

console.log("runnning tests");

/*QUnit.jUnitReport = function(report) {
	console.log("writing report");
    qunitXmlContainer = report.xml;
//    console.log(report.xml);
};*/

QUnit.module( "qeryStringFunc" ); 
QUnit.test( "should return an array of query strings contained in url", function( assert ) {
	pageScript = new PageScript(test)
	var loc = { location: { search: "?something=y&otherthing=q&something=x&something=z" } } 
	var data={}
	data["something"]=["y","x","z"];
	data["otherthing"]="q";
	var qs = QueryStringFunc( loc );
	
	assert.equal(JSON.stringify(qs),JSON.stringify(data), "the arrays should equal" );
})

}

//t.testCollection.call(t)
	var scriptContainer=t.document.createElement('script')
    scriptContainer.setAttribute("type","text/javascript")
	scriptContainer.innerHTML="("+testCollection.toString()+"())"
	t.document.getElementsByTagName("head")[0].appendChild(scriptContainer)
}

tfrwrk.loadPage("fiokom.html",account_uTest)