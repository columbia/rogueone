require('lib')
o = {
	f: function(){
		this.f = function(){
			return 1
		}
		return 0
	}
}
lib.api(o.f())
lib.api(o.f())
