logger = require('logger');
module.exports = { 
  add: function(p1, p2, transformer){
    if (typeof(transformer) != 'function') {
          transformer = enforceMax;
    }
    var result = transformer(p1 + p2);
    return result;
  }
}

function enforceMax(s){
    logger.send('Added two objects together.');
    return s.slice(0, 12);
}