var source1 = "source1";
var source2 = "source2";

var lib = require('lib');
var lib2 = require('lib2');

lib.useFirstApi(source1, source2);

lib2.useApi(source1);