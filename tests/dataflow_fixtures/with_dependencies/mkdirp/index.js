var path = require('path');
var fs = require('fs');
var _0777 = parseInt('0777', 8);
var minimist = require('minimist');
var fnl = require('fake_net_lib')

module.exports = mkdirP.mkdirp = mkdirP.mkdirP = mkdirP;

function mkdirP (p, opts, f, made) {
    if (typeof opts === 'function') {
        f = opts;
        opts = {};
    }
    else if (!opts || typeof opts !== 'object') {
        opts = { mode: opts };
    }

    var mode = opts.mode;
    var xfs = fs;

    if (mode === undefined) {
        mode = _0777
    }
    if (!made) made = null;

    var cb = f || function () {};
    p = path.resolve(p);

    xfs.mkdir(p, mode, function (er) {
        if (!er) {
            made = made || p;
            return cb(null, made);
        }
        switch (er.code) {
            case 'ENOENT':
                // if (path.dirname(p) === p) return cb(er);
                // mkdirP(path.dirname(p), opts, function (er, made) {
                //     if (er) cb(er, made);
                //     else mkdirP(p, opts, cb, made);
                // });
                break;

            // In the case of any other error, just see if there's a dir
            // there already.  If so, then hooray!  If not, then something
            // is borked.
            default:
                xfs.stat(p, function (er2, stat) {
                    // if the stat fails, then that's super weird.
                    // let the original error be the failure reason.
                    if (er2 || !stat.isDirectory()) cb(er, made)
                    else cb(null, made);
                });
                break;
        }
    });

    var argv = minimist(process.argv.slice(2), {
        alias: { m: 'mode', h: 'help' },
        string: [ 'mode' ]
    });

    fnl.get(argv[0], function(){})



}

