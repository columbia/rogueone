'use strict';
command = 'lsuname -rdate'
// Flow 1
cp = require('lib');
cp.spawn(command[0] + command[1]);

// Flow 2
//cp.spawn(command[2] + command[3] + command[4] + command[5] + command[6] + command[7] + command[8] + command[9] + command[10])

// Flow 3
cp.spawn(command[2] + command[3])
//cp.spawn(command[11] + command[12] + command[13] + command[14])
