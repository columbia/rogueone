
lib = require('externalLib')
o = {
	f: function(){
		return 1
	}
}
lib.api(o.f())
o.f = function(){
	return 2
}
lib.api(o.f())
