'use strict';
// Flow 1
Object.prototype.holder = require('lib').getInstance().source;
o2 = {};
require('sink').sink(o2.holder);

