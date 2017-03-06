var jsdom = require("jsdom").jsdom;
var document = jsdom("<html><body></body></html>");
var p = document.createElement("p");
document.body.appendChild(p);
document.getElementsByTagName("p").innerHTML = "******** jsdom DOM test ready ********";
console.log(document.getElementsByTagName("p").innerHTML)
