#!/usr/bin/env node

const nrl = require('npm-remote-ls')
done = false
fs = require('fs')
nrl.config({
    development: false,
    optional: false
})
name = process.argv[2]
version = process.argv[3]
cb = function (data) {
    process.stdout.write(JSON.stringify(data));
    process.stdout.write("\n")
    done = true
}
if (process.argv.length <= 4 || process.argv[4].length === 0) {

    nrl.ls(name, version, true, cb)
} else {
    package_json_path = process.argv[4];
    var ls = new nrl.RemoteLS();
    package_json = JSON.parse(fs.readFileSync(package_json_path));
    console.assert(package_json['name'] == name);
    console.assert(package_json['version'] == version);

	if (package_json['dependencies'] == undefined){
			ls.queue.push({
				name: name,
				version: version,
				parent: ls.tree
			})
		ls.queue.drain = function () {
			cb(Object.keys(ls.flat))
		}

	} else{

		for (d in package_json['dependencies']) {
			ls.queue.push({
				name: d,
				version: package_json['dependencies'][d],
				parent: ls.tree
			})

		}
		ls.queue.drain = function () {
			cb(Object.keys(ls.flat))
		}
	}
	ls.queue.resume()
	
    // ls.ls(name, version, function () {
    //     cb([].concat([name + '@' + version], Object.keys(ls.flat)))
    // })
}
/*
function waitForDone() {
    if (!done) {
        setTimeout(waitForDone, 1)
    }
}
waitForDone()*/
