secret = process.env['SECRET_KEY'];
secLib = require('secure-store');
secClient = secLib.init({"key": secret})
pubClient = require('public-store');
result = secClient.query('User Query');
pubClient.publish(result.publicData);