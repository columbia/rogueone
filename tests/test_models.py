from fast.manager.registry import *
from fast.manager.models import *
from fast.manager.engine import init as init_engine
from pathlib import Path

single_v_folder = os.path.join(os.path.dirname(__file__), "dataflow_fixtures", "single_version")
semver_deps = ['semver@5.1.0', 'tap@2.3.4', 'js-yaml@3.14.1', 'glob@6.0.4', 'mkdirp@0.5.6', 'opener@1.5.2', 
        'readable-stream@2.3.8', 'codecov.io@0.1.6', 'signal-exit@2.1.2', 'deeper@2.1.0', 'foreground-child@1.5.6', 
        'supports-color@1.3.1', 'nyc@3.2.2', 'coveralls@2.13.3', 'only-shallow@1.2.0', 'inflight@1.0.6', 'inherits@2.0.4', 
        'argparse@1.0.10', 'esprima@4.0.1', 'path-is-absolute@1.0.1', 'once@1.4.0', 'core-util-is@1.0.3', 'minimist@1.2.8', 'minimatch@3.1.2', 'tap-mocha-reporter@0.0.27', 'isarray@1.0.0', 'tap-parser@1.3.2', 'tmatch@1.0.2', 'safe-buffer@5.1.2', 'string_decoder@1.1.1', 'process-nextick-args@2.0.1', 'util-deprecate@1.0.2', 'foreground-child@1.3.0', 'signal-exit@3.0.7', 'glob@5.0.15', 'lodash@3.10.1', 'urlgrey@0.4.0', 'cross-spawn@4.0.2', 'istanbul@0.3.22', 'strip-bom@2.0.0', 'js-yaml@3.6.1', 'request@2.42.0', 'yargs@3.32.0', 'minimist@1.2.0', 'rimraf@2.7.1', 'request@2.79.0', 'sprintf-js@1.0.3', 'brace-expansion@1.1.11', 'diff@1.4.0', 'lcov-parse@0.0.10', 'debug@2.6.9', 'escape-string-regexp@1.0.5', 'log-driver@1.2.5', 'wrappy@1.0.2', 'glob@7.2.3', 'readable-stream@1.1.14', 'color-support@1.1.3', 'unicode-length@1.0.3', 'spawn-wrap@1.4.3', 'events-to-array@1.1.2', 'lru-cache@4.1.5', 'which@1.3.1', 'abbrev@1.0.9', 'tape@2.3.0', 'async@1.5.2', 'esprima@2.5.0', 'handlebars@4.7.7', 'nopt@3.0.6', 'resolve@1.1.7', 'wordwrap@1.0.0', 'supports-color@3.2.3', 'is-utf8@0.2.1', 'esprima@2.7.3', 'fileset@0.2.1', 'caseless@0.6.0', 'forever-agent@0.5.2', 'json-stringify-safe@5.0.1', 'bl@0.9.5', 'escodegen@1.7.1', 'mime-types@1.0.2', 'qs@1.2.2', 'tunnel-agent@0.4.3', 'node-uuid@1.4.8', 'oauth-sign@0.4.0', 'http-signature@0.10.1', 'aws-sign2@0.5.0', 'tough-cookie@4.1.3', 'form-data@0.1.4', 'hawk@1.1.1', 'decamelize@1.2.0', 'cliui@3.2.0', 'camelcase@2.1.1', 'window-size@0.1.4', 'aws-sign2@0.6.0', 'string-width@1.0.2', 'y18n@3.2.2', 'aws4@1.12.0', 'caseless@0.11.0', 'forever-agent@0.6.1', 'extend@3.0.2', 'combined-stream@1.0.8', 'har-validator@2.0.6', 'hawk@3.1.3', 'stringstream@0.0.6', 'form-data@2.1.4', 'is-typedarray@1.0.0', 'http-signature@1.1.1', 'isstream@0.1.2', 'os-locale@1.4.0', 'oauth-sign@0.8.2', 'mime-types@2.1.35', 'balanced-match@1.0.2', 'concat-map@0.0.1', 'tough-cookie@2.3.4', 'ms@2.0.0', 'fs.realpath@1.0.0', 'qs@6.3.3', 'isarray@0.0.1', 'string_decoder@0.10.31', 'punycode@1.4.1', 'strip-ansi@3.0.1', 'os-homedir@1.0.2', 'yallist@2.1.2', 'uuid@3.4.0', 'isexe@2.0.0', 'defined@0.0.0', 'through@2.3.8', 'split@0.2.10', 'neo-async@2.6.2', 'pseudomap@1.0.2', 'source-map@0.6.1', 'jsonify@0.0.1', 'abbrev@1.1.1', 'has-flag@1.0.0', 'deep-equal@0.1.2', 'resumer@0.0.0', 'minimatch@2.0.10', 'stream-combiner@0.0.4', 'esutils@2.0.3', 'uglify-js@3.17.4', 'estraverse@1.9.3', 'readable-stream@1.0.34', 'esprima@1.2.5', 'source-map@0.2.0', 'assert-plus@0.1.5', 'asn1@0.1.11', 'punycode@2.3.0', 'universalify@0.2.0', 'psl@1.9.0', 'combined-stream@0.0.7', 'async@0.9.2', 'optionator@0.5.0', 'cryptiles@0.2.2', 'ctype@0.5.3', 'url-parse@1.5.10', 'wrap-ansi@2.1.0', 'code-point-at@1.1.0', 'mime@1.2.11', 'is-fullwidth-code-point@1.0.0', 'boom@0.4.2', 'hoek@0.9.1', 'delayed-stream@1.0.0', 'chalk@1.1.3', 'sntp@0.2.4', 'pinkie-promise@2.0.1', 'boom@2.10.1', 'hoek@2.16.3', 'sntp@1.0.9', 'commander@2.20.3', 'is-my-json-valid@2.20.6', 'cryptiles@2.0.5',
        'asynckit@0.4.0', 'assert-plus@0.2.0', 'jsprim@1.4.2', 'lcid@1.0.0', 'ansi-regex@2.1.1', 'mime-db@1.52.0', 'sshpk@1.17.0', 'delayed-stream@0.0.5', 'wordwrap@0.0.3', 'deep-is@0.1.4', 'type-check@0.3.2', 'levn@0.2.5', 'fast-levenshtein@1.0.7', 'querystringify@2.2.0', 'duplexer@0.1.2', 'ansi-styles@2.2.1', 'has-ansi@2.0.0', 'amdefine@1.0.1', 'prelude-ls@1.1.2', 'supports-color@2.0.0', 'pinkie@2.0.4', 'requires-port@1.0.0', 'assert-plus@1.0.0', 'xtend@4.0.2', 'number-is-nan@1.0.1', 'extsprintf@1.3.0', 'json-schema@0.4.0', 'verror@1.10.0', 'invert-kv@1.0.0', 'asn1@0.2.6', 'generate-function@2.3.1', 'generate-object-property@1.2.0', 'dashdash@1.14.1', 'getpass@0.1.7', 'is-my-ip-valid@1.0.1', 'jsbn@0.1.1', 'safer-buffer@2.1.2', 'jsonpointer@5.0.1', 'tweetnacl@0.14.5', 'bcrypt-pbkdf@1.0.2', 'ecc-jsbn@0.1.2', 'core-util-is@1.0.2', 'extsprintf@1.4.1', 'is-property@1.0.2']

def test_save_deps():
    # Set up version model for semver
    engine, Session = init_engine(echo=False)
    session = Session(autoflush=False)
    p = Package(name='semver')
    v = Version(package=p, number='5.1.0')
    session.add(v)
    session.commit()
    assert v.id
    v.save_dependencies(session, semver_deps)
    session.commit()
    session.expire_all()

    assert len(v.dependencies) == len(semver_deps)
    v2 = session.query(Version).filter(Version.id == v.id).one()
    assert len(v2.dependencies) == len(semver_deps)
    assert len(v2.dependents) == 1
    assert len(session.query(DependentDependency).all()) == len(semver_deps)

def test_dep_cache():
    engine, Session = init_engine(echo=False)
    session = Session(autoflush=False)
    p = Package(name='semver')
    v = Version(package=p, number='5.1.0', disk_location=str(Path(single_v_folder) / 'dep_cache_test'))
    Path(v.dependency_cache_path()).unlink(missing_ok=True)
    success, deps = v.get_cached_dependencies()
    assert not success
    session.add(v)
    session.commit()
    assert v.id
    v.save_dependencies_to_cache(semver_deps)

    success, deps = v.get_cached_dependencies()
    assert success