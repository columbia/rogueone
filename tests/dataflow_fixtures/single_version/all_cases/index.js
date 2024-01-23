// A: Static data, explicitly defined objects
// B: Parameters to module exports
// C: Parameters to passed out callbacks
// D: API return values and system values (fs)
// E: Wildcard/symbolic objects

// Case 0, no external flow at all.
zero_source = 'zerosource'
zero_sink = zero_source[0] + zero_source[1] + zero_source.replace('source', 'sink')

// Example group 1.  No property references,
// Simplest instances of all 5 cases with an unknown api sink
lib = require('lib')

// Case 1.a
sourceA = "sourceAstr"
lib.api1(sourceA)

// Case 1.b
module.exports = {
    "case1b": function (sourceB) {extend
        lib.api2(sourceB)
    }
}

// Case 1.c
lib.api3(function(sourceC){
    lib.api4(sourceC)
})

// Case 1.d
fs = require('fs')
lib.api5(lib.midApi('/etc/shadow'))

// Case 1.e
sourceE = "ls uname -r"
lib.api6(sourceE[0] + sourceE[1])

result = lib.api1a("sourceXstr") + lib.api1b("sourceYstr")

result2 = lib.sublib.api1c("sourceXstr2") + lib.sublib2.api1d("sourceYstr2")

result3 = lib.sublib.api1e("ref1").prop("ref2")

result4 = lib.api1f("source1", "source2")

result5 = lib.api1f("source3", "source4")
/* ********************************
 Example Group 2
 Different property reference types into a simple API
 */
obj = fs.statSync('/etc/statshadow')
// Example 2.A, simple source of a return value object
lib.api7(obj)
// Example 2.B, one property of a return value object
lib.api8(obj["birthtimeMs"])
// Example 2.C, one property of an array
keyList = [
  "dev",
  "uid",
  "gid",
  "rdev",
  "blksize",
  "ino",
  "size",
    ]
lib.api9(keyList[0])

// Example 2.D, one property of an array, referred to by a property of another property
lib.api10(keyList[keyList[2].length])

// Example 2.E, result of binop of various sub objects
lib.api11(keyList[1][0] + keyList[2][1] + keyList[0][0])