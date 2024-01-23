// Excerpted from jasmine: lib/command.js
// Use of fs in benign version:
var path = require('lib')

path.join(
	process.cwd(),
	'node_modules',
	'avo',
	'dist',
	getAssetForOs(os.platform())
)
