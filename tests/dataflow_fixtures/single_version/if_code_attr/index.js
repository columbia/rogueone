'use strict';
// Bad runtime require
cp = require('child_process');

if(cp.something() > 5){
    cp.spawn('ls')
} else {
    console.log('hey')
}
