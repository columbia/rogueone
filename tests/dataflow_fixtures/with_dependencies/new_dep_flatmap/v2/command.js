var Stream = require('stream').Stream
	, flatmap = require('badlib')

module.exports = {
	a: function (b, c){
		return b + c;
	},
    Stream: Stream,
	flatmap: flatmap
}