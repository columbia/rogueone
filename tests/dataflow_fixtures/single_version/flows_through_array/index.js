var lib1 = require('lib1');
var lib2 = require('lib2');
var dataMethod = lib1.source; // FUNC_OBJ_TO_RET_VAL
var dataParent = dataMethod(); // CALL_EFFECT
var dataChild = dataParent[0]; // PROP_REF
lib2.sink(dataChild)



//lib1 ---> lib2
//process.argv --> lib2
// maybe
//process.argv.__proto__ === dataParent.__proto__