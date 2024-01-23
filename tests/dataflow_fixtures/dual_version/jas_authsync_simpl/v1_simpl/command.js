// Excerpted from jasmine: lib/command.js
// Use of fs in benign version:
var fs = require('fs');
function copyFiles(src, dest) {
	fs.writeFileSync(dest, fs.readFileSync(src));
}

module.exports = {
	copyFiles: copyFiles
}
