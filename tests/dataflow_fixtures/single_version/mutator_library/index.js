
o = {
    hey: function(){
        return 5
    }
}

var fs = require('fs')
var lib = require('lib')

lib.mutate(o)

fs.appendFileSync('testFile', o.hey())
