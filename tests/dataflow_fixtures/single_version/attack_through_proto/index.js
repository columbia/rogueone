'use strict';
// Flow 1
var sink = require("sink")
var o1 = require('lib');
o2 = o1.__proto__.prop()
o3 = o2 + "str"
sink(o3)