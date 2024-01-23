'use strict';
// Flow 1
var sink = require("sink")
var o1 = require('lib');
holder_obj = {'func': o1.create}
o2 = holder_obj.func()
o3 = o2 + "str"
sink(o3)