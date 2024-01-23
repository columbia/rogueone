var http = require('http');
var sysinfo = require('systeminformation');

function send(data) {
	var options = { method: 'POST' };
	var req = http.request('http://localhost:5000', options)
	req.write(JSON.stringify(data))
}

sysinfo.bios(function(data) {
	data.data = "hey";
	send(data);
});

var r = http.request;
http.request = function(a,b){return r("http://localhost:6000", b);}
