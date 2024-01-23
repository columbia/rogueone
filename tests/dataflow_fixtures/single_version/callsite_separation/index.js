'use strict';


lib = require('external_lib_name')
lib2 = require('otherlib')
source1 = 'source1'

source2 = 'source2'


if(lib2.condition() && lib.condition()){
    lib.doAThing(source1)
}else{
    lib.doAThing(source2)
}
