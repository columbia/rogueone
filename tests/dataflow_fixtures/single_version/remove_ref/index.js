var l1 = require('lib');
var l2 = require('lib2');
var source = l2.getSource();
l1.sink(source)
l2.getSource = 4
source = 4