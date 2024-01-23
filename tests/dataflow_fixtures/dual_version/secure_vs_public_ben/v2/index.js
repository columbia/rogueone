secret = process.env['SECRET_KEY'];
secureLib = require('secure-store');
publicLib = require('public-store');

secureClient = secureLib.init();
publicClient = publicLib.init();
secureClient.key = secret;
result = secureClient.query('User Query');
if(result.success){
    publicClient.publish("Query successful in " + result.runTime.toString() + "seconds.")
    publicClient.publish(result.data);
} else{
    publicClient.publish("Query Failed.")
}