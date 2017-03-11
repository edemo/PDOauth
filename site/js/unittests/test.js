var QUnit = require ('qunit-cli');
QUnit.load();

console.log("hello world")
QUnit.module( "test" ); 
QUnit.test( "basic environment test", function( assert ) {
        assert.equal("1","1");
})
