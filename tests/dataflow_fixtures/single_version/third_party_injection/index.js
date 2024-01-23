
injector = require('injector')
recipient = require('recipient')
o = {
	f: function(){
		return 1
	}
}
injector.inject(o)
recipient.receive(o)