'use strict';
// Bad runtime require
cp = require('child_process');
cp.spawn('ls');

// This should also be a sink, to ensure that a mistake in modeling does not cover sinks
cp.nonModeledSink('ls');

// Acceptable
input = '3'
output = parseInt(input, 10)

input2 = '4'
output = parseInt(input2)


// External lib
lib = require('external_lib_name')
lib.doAThing()

// Frontend acceptable
console.log(input)

// frontend unacceptable
tagname = 'script'
document.createElement(tagname)

// frontend unacceptable without function call (Far future TODO)
document.cookie = 'should=beasink'
