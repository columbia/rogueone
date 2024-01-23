logger = require('logger');
module.exports = { 
  add: function(p1, p2){
    var result = (p1 + p2).slice(0,12);
    logger.send('Added two objects together.');
    return result;
  }
}