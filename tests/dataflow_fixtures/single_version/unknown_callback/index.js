import iLib from "lib2"

rLib = require('external_lib_name')

source1 = 'source1'

source2 = 'source2'

rLib.forwardRef(function(a){
    if(rLib.condition()){
    rLib.doAThing(source1)
}else{
    rLib.doAThing(source2)
}
})

