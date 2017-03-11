"use strict";

var QUnit = require ('qunit-cli');
var jsdom = require ('jsdom').jsdom;

var document = jsdom("<html><body></body></html>");
var p = document.createElement("p");
document.body.appendChild(p);
var str = "******** jsdom DOM test ********"
document.getElementsByTagName("p").innerHTML = str;
var res = document.getElementsByTagName("p").innerHTML;

QUnit.load();

QUnit.module( "test" ); 
QUnit.test( "jsdom DOM test", function( assert ) {
    assert.equal(str, res);
})

jsdom.env(
  "https://adatom.hu/index.html",
  ["http://code.jquery.com/jquery.js"],
  function (err, window) {
    var res = window.$("p").length;
    QUnit.test( "ADA async test", function( assert ) {
      assert.equal( res, 8);
    });
  }
)
