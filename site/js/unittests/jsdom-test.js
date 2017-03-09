"use strict";

var jsdom = require("jsdom").jsdom;
var document = jsdom("<html><body></body></html>");
var p = document.createElement("p");
document.body.appendChild(p);
var str = "******** jsdom DOM test ********"
document.getElementsByTagName("p").innerHTML = str;
var res = document.getElementsByTagName("p").innerHTML;

QUnit.module( "test" ); 
QUnit.test( "jsdom DOM test", function( assert ) {
	assert.equal(str, res, "na" );
})
