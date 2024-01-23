/*!
 * 
 * SpreadJS Wrapper Components for Vue 14.2.6
 * 
 * Copyright(c) GrapeCity, Inc.  All rights reserved.
 * 
 * Licensed under the SpreadJS Commercial License.
 * us.sales@grapecity.com
 * http://www.grapecity.com/licensing/grapecity/
 * 
 */
(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory(require("vue"), require("@grapecity/spread-sheets"), require("@grapecity/spread-sheets-designer"));
	else if(typeof define === 'function' && define.amd)
		define(["vue", "@grapecity/spread-sheets", "@grapecity/spread-sheets-designer"], factory);
	else if(typeof exports === 'object')
		exports["SpreadSheetsDesignerComponents"] = factory(require("vue"), require("@grapecity/spread-sheets"), require("@grapecity/spread-sheets-designer"));
	else
		root["SpreadSheetsDesignerComponents"] = factory(root["vue"], root["@grapecity/spread-sheets"], root["@grapecity/spread-sheets-designer"]);
})(this, function(__WEBPACK_EXTERNAL_MODULE_3__, __WEBPACK_EXTERNAL_MODULE_5__, __WEBPACK_EXTERNAL_MODULE_6__) {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});

	var _Designer = __webpack_require__(1);

	var _Designer2 = _interopRequireDefault(_Designer);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	exports.default = _Designer2.default;

/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});

	var _vueNameSpace = __webpack_require__(2);

	var _vueNameSpace2 = _interopRequireDefault(_vueNameSpace);

	var _spreadNameSpace = __webpack_require__(4);

	var _spreadNameSpace2 = _interopRequireDefault(_spreadNameSpace);

	__webpack_require__(6);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var DESIGNER_TAG_NAME = 'gc-spread-sheets-designer';
	_vueNameSpace2.default.component(DESIGNER_TAG_NAME, {
	  props: ['config', 'styleInfo', 'spreadOptions'],
	  data: function data() {
	    return {
	      _designer_styleInfo: null,
	      _designer_config: null,
	      _designer: null,
	      _spreadOptions: null
	    };
	  },

	  render: function render(createElement) {
	    return createElement('div');
	  },
	  methods: {
	    _designerInitialize: function _designerInitialize() {
	      this._designer_styleInfo = this.$props.styleInfo || null;
	      this._designer_config = this.$props.config || null;
	      this._spreadOptions = this.$props.spreadOptions || null;
	      this._setStyle(this._designer_styleInfo);
	      this._designer = new _spreadNameSpace2.default.Spread.Sheets.Designer.Designer(this.$el, this._designer_config, undefined, this._spreadOptions);
	    },
	    _setStyle: function _setStyle(newStyle) {
	      for (var key in newStyle) {
	        this.$el.style[key] = newStyle[key];
	      }
	    }
	  },
	  mounted: function mounted() {
	    this._designerInitialize();
	    this.$emit('designerInitialized', this._designer);
	  },
	  destroyed: function destroyed() {
	    this._designer.destroy();
	    this._designer = null;
	  },

	  watch: {
	    config: {
	      handler: function handler(val, oldVal) {
	        this._designer_config = val;
	        this._designer.setConfig(this._designer_config);
	        this._designer.refresh();
	      }
	    },
	    'styleInfo.width': {
	      handler: function handler(val, oldVal) {
	        this.$el.style['width'] = val;
	        this._designer.refresh();
	      }
	    },
	    'styleInfo.height': {
	      handler: function handler(val, oldVal) {
	        this.$el.style['height'] = val;
	        this._designer.refresh();
	      }
	    },
	    styleInfo: {
	      deep: true,
	      handler: function handler(val, oldVal) {
	        this._setStyle(val);
	        this._designer.refresh();
	      }
	    }
	  }
	});
	exports.default = _vueNameSpace2.default.options.components['gc-spread-sheets-designer'];

/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});

	var _vue = __webpack_require__(3);

	var _vue2 = _interopRequireDefault(_vue);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	exports.default = _vue2.default;

/***/ }),
/* 3 */
/***/ (function(module, exports) {

	module.exports = __WEBPACK_EXTERNAL_MODULE_3__;

/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});

	var _spreadSheets = __webpack_require__(5);

	var _spreadSheets2 = _interopRequireDefault(_spreadSheets);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	exports.default = _spreadSheets2.default;

/***/ }),
/* 5 */
/***/ (function(module, exports) {

	module.exports = __WEBPACK_EXTERNAL_MODULE_5__;

/***/ }),
/* 6 */
/***/ (function(module, exports) {

	module.exports = __WEBPACK_EXTERNAL_MODULE_6__;

/***/ })
/******/ ])
});
;