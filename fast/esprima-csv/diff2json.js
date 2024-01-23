#!/usr/bin/env node


const d2h = require('diff2html');

var fs = require('fs');
var stdinBuffer = String(fs.readFileSync(0))

process.stdout.write(JSON.stringify(d2h.parse(stdinBuffer)))
process.stdout.write("\n")
