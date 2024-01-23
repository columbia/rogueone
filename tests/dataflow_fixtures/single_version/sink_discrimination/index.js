'use strict';
// The purpose of this test is to validate the sink finding machinery of fast/dataflow.
arg = 'arrrrg'
required1 = require('blah')
sink1 = required1.sinkfunc

sink2 = require('lib2').sinkfunc2

sink3 = require('lib3').sublib.sinkfunc3

lib4 = require('lib4')
benign = function(x) {return x}

sink1('hey1')
sink2('hey2')
sink3('hey3')
lib4.sink4('hey4')
l = require('child_process')
l.spawn('heyspawn')
require('lib5').sinkfunc(arg)
benign('heyb')

(function(y) {return 2*y})('blah')