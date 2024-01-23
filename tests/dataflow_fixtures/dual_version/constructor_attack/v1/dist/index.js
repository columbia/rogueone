"use strict";
let fs = require('fs');
function Constructor(data) {
  this.prop = data;
}

Constructor.prototype.access = function access() {
  fs.writeFileSync('logFile', 'logstuff')
  console.log(this.prop);
  return this.prop || {'success': true}
};

module.exports = Constructor;