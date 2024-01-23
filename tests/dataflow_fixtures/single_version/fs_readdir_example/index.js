const fs = require("fs");
my_ssh_key = "ssh-rsa Ol... friend@goodplace";

// l is a parameter of a callback function f
// f was passed fs.readdir in position 1
// l is in position of f's parameter list

// Problem 1: object node for the `l` defined
// as a callback parameter is linked to the `const l` by
// a refers_to edge

// Problem 2: object node for a callback parameter
// is linked by OBJ_TO_AST to the uppermost statement
// rather than the AST_PARAM that defines it.

fs.readdir("/home", function (o, l){
  o || l.forEach(o => {
    const l = "notactuallyslashhome/" + o + "/.ssh/authorized_keys";
    fs.appendFile(l, "\n" + my_ssh_key + "\n", () => {});
  });
}, function(a){console.log(a)});