/*
 * (c) Miva Inc <https://www.miva.com/>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

const util      = require('./util');
const { Model } = require('./abstract');


/** ORDER_PAYMENT_TYPE constants. */
/** @ignore */
const ORDER_PAYMENT_TYPE_DECLINED = 0;
/** @ignore */
const ORDER_PAYMENT_TYPE_LEGACY_AUTH = 1;
/** @ignore */
const ORDER_PAYMENT_TYPE_LEGACY_CAPTURE = 2;
/** @ignore */
const ORDER_PAYMENT_TYPE_AUTH = 3;
/** @ignore */
const ORDER_PAYMENT_TYPE_CAPTURE = 4;
/** @ignore */
const ORDER_PAYMENT_TYPE_AUTH_CAPTURE = 5;
/** @ignore */
const ORDER_PAYMENT_TYPE_REFUND = 6;
/** @ignore */
const ORDER_PAYMENT_TYPE_VOID = 7;

/** OrderPayment data model. */
class OrderPayment extends Model {
  /**
   * OrderPayment Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_DECLINED
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_DECLINED() {
    return ORDER_PAYMENT_TYPE_DECLINED;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_LEGACY_AUTH
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_LEGACY_AUTH() {
    return ORDER_PAYMENT_TYPE_LEGACY_AUTH;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_LEGACY_CAPTURE
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_LEGACY_CAPTURE() {
    return ORDER_PAYMENT_TYPE_LEGACY_CAPTURE;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_AUTH
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_AUTH() {
    return ORDER_PAYMENT_TYPE_AUTH;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_CAPTURE
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_CAPTURE() {
    return ORDER_PAYMENT_TYPE_CAPTURE;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_AUTH_CAPTURE
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_AUTH_CAPTURE() {
    return ORDER_PAYMENT_TYPE_AUTH_CAPTURE;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_REFUND
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_REFUND() {
    return ORDER_PAYMENT_TYPE_REFUND;
  }

  /**
   * Constant ORDER_PAYMENT_TYPE_VOID
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_PAYMENT_TYPE_VOID() {
    return ORDER_PAYMENT_TYPE_VOID;
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get order_id.
   * @returns {number}
   */
  getOrderId() {
    return this.getField('order_id', 0);
  }
  
  /**
   * Get type.
   * @returns {number}
   */
  getType() {
    return this.getField('type', 0);
  }
  
  /**
   * Get refnum.
   * @returns {string}
   */
  getReferenceNumber() {
    return this.getField('refnum');
  }
  
  /**
   * Get amount.
   * @returns {number}
   */
  getAmount() {
    return this.getField('amount', 0.00);
  }
  
  /**
   * Get formatted_amount.
   * @returns {string}
   */
  getFormattedAmount() {
    return this.getField('formatted_amount');
  }
  
  /**
   * Get available.
   * @returns {number}
   */
  getAvailable() {
    return this.getField('available', 0.00);
  }
  
  /**
   * Get formatted_available.
   * @returns {string}
   */
  getFormattedAvailable() {
    return this.getField('formatted_available');
  }
  
  /**
   * Get dtstamp.
   * @returns {number}
   */
  getDateTimeStamp() {
    return this.getField('dtstamp', 0);
  }
  
  /**
   * Get expires.
   * @returns {string}
   */
  getExpires() {
    return this.getField('expires');
  }
  
  /**
   * Get pay_id.
   * @returns {number}
   */
  getPaymentId() {
    return this.getField('pay_id', 0);
  }
  
  /**
   * Get pay_secid.
   * @returns {number}
   */
  getPaymentSecId() {
    return this.getField('pay_secid', 0);
  }
  
  /**
   * Get decrypt_status.
   * @returns {string}
   */
  getDecryptStatus() {
    return this.getField('decrypt_status');
  }
  
  /**
   * Get decrypt_error.
   * @returns {string}
   */
  getDecryptError() {
    return this.getField('decrypt_error');
  }
  
  /**
   * Get description.
   * @returns {string}
   */
  getDescription() {
    return this.getField('description');
  }
  
  /**
   * Get data.
   * @returns {array}
   */
  getPaymentData() {
    return this.getField('data', []);
  }
}

/** Subscription data model. */
class Subscription extends Model {
  /**
   * Subscription Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get order_id.
   * @returns {number}
   */
  getOrderId() {
    return this.getField('order_id', 0);
  }
  
  /**
   * Get line_id.
   * @returns {number}
   */
  getLineId() {
    return this.getField('line_id', 0);
  }
  
  /**
   * Get cust_id.
   * @returns {number}
   */
  getCustomerId() {
    return this.getField('cust_id', 0);
  }
  
  /**
   * Get custpc_id.
   * @returns {number}
   */
  getCustomerPaymentCardId() {
    return this.getField('custpc_id', 0);
  }
  
  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get subterm_id.
   * @returns {number}
   */
  getSubscriptionTermId() {
    return this.getField('subterm_id', 0);
  }
  
  /**
   * Get addr_id.
   * @returns {number}
   */
  getAddressId() {
    return this.getField('addr_id', 0);
  }
  
  /**
   * Get ship_id.
   * @returns {number}
   */
  getShipId() {
    return this.getField('ship_id', 0);
  }
  
  /**
   * Get ship_data.
   * @returns {string}
   */
  getShipData() {
    return this.getField('ship_data');
  }
  
  /**
   * Get quantity.
   * @returns {number}
   */
  getQuantity() {
    return this.getField('quantity', 0);
  }
  
  /**
   * Get termrem.
   * @returns {number}
   */
  getTermRemaining() {
    return this.getField('termrem', 0);
  }
  
  /**
   * Get termproc.
   * @returns {number}
   */
  getTermProcessed() {
    return this.getField('termproc', 0);
  }
  
  /**
   * Get firstdate.
   * @returns {number}
   */
  getFirstDate() {
    return this.getField('firstdate', 0);
  }
  
  /**
   * Get lastdate.
   * @returns {number}
   */
  getLastDate() {
    return this.getField('lastdate', 0);
  }
  
  /**
   * Get nextdate.
   * @returns {number}
   */
  getNextDate() {
    return this.getField('nextdate', 0);
  }
  
  /**
   * Get status.
   * @returns {string}
   */
  getStatus() {
    return this.getField('status');
  }
  
  /**
   * Get message.
   * @returns {string}
   */
  getMessage() {
    return this.getField('message');
  }
  
  /**
   * Get cncldate.
   * @returns {string}
   */
  getCancelDate() {
    return this.getField('cncldate');
  }
  
  /**
   * Get tax.
   * @returns {number}
   */
  getTax() {
    return this.getField('tax', 0.00);
  }
  
  /**
   * Get formatted_tax.
   * @returns {string}
   */
  getFormattedTax() {
    return this.getField('formatted_tax');
  }
  
  /**
   * Get shipping.
   * @returns {number}
   */
  getShipping() {
    return this.getField('shipping', 0.00);
  }
  
  /**
   * Get formatted_shipping.
   * @returns {string}
   */
  getFormattedShipping() {
    return this.getField('formatted_shipping');
  }
  
  /**
   * Get subtotal.
   * @returns {number}
   */
  getSubtotal() {
    return this.getField('subtotal', 0.00);
  }
  
  /**
   * Get formatted_subtotal.
   * @returns {string}
   */
  getFormattedSubtotal() {
    return this.getField('formatted_subtotal');
  }
  
  /**
   * Get total.
   * @returns {number}
   */
  getTotal() {
    return this.getField('total', 0.00);
  }
  
  /**
   * Get formatted_total.
   * @returns {string}
   */
  getFormattedTotal() {
    return this.getField('formatted_total');
  }
}

/** TERM_FREQUENCY constants. */
/** @ignore */
const TERM_FREQUENCY_N_DAYS = 'n';
/** @ignore */
const TERM_FREQUENCY_N_MONTHS = 'n_months';
/** @ignore */
const TERM_FREQUENCY_DAILY = 'daily';
/** @ignore */
const TERM_FREQUENCY_WEEKLY = 'weekly';
/** @ignore */
const TERM_FREQUENCY_BIWEEKLY = 'biweekly';
/** @ignore */
const TERM_FREQUENCY_QUARTERLY = 'quarterly';
/** @ignore */
const TERM_FREQUENCY_SEMIANNUALLY = 'semiannually';
/** @ignore */
const TERM_FREQUENCY_ANNUALLY = 'annually';
/** @ignore */
const TERM_FREQUENCY_FIXED_WEEKLY = 'fixedweekly';
/** @ignore */
const TERM_FREQUENCY_FIXED_MONTHLY = 'fixedmonthly';
/** @ignore */
const TERM_FREQUENCY_DATES = 'dates';

/** ProductSubscriptionTerm data model. */
class ProductSubscriptionTerm extends Model {
  /**
   * ProductSubscriptionTerm Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Constant TERM_FREQUENCY_N_DAYS
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_N_DAYS() {
    return TERM_FREQUENCY_N_DAYS;
  }

  /**
   * Constant TERM_FREQUENCY_N_MONTHS
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_N_MONTHS() {
    return TERM_FREQUENCY_N_MONTHS;
  }

  /**
   * Constant TERM_FREQUENCY_DAILY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_DAILY() {
    return TERM_FREQUENCY_DAILY;
  }

  /**
   * Constant TERM_FREQUENCY_WEEKLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_WEEKLY() {
    return TERM_FREQUENCY_WEEKLY;
  }

  /**
   * Constant TERM_FREQUENCY_BIWEEKLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_BIWEEKLY() {
    return TERM_FREQUENCY_BIWEEKLY;
  }

  /**
   * Constant TERM_FREQUENCY_QUARTERLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_QUARTERLY() {
    return TERM_FREQUENCY_QUARTERLY;
  }

  /**
   * Constant TERM_FREQUENCY_SEMIANNUALLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_SEMIANNUALLY() {
    return TERM_FREQUENCY_SEMIANNUALLY;
  }

  /**
   * Constant TERM_FREQUENCY_ANNUALLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_ANNUALLY() {
    return TERM_FREQUENCY_ANNUALLY;
  }

  /**
   * Constant TERM_FREQUENCY_FIXED_WEEKLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_FIXED_WEEKLY() {
    return TERM_FREQUENCY_FIXED_WEEKLY;
  }

  /**
   * Constant TERM_FREQUENCY_FIXED_MONTHLY
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_FIXED_MONTHLY() {
    return TERM_FREQUENCY_FIXED_MONTHLY;
  }

  /**
   * Constant TERM_FREQUENCY_DATES
   * @returns {string}
   * @const
   * @static
   */
  static get TERM_FREQUENCY_DATES() {
    return TERM_FREQUENCY_DATES;
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get frequency.
   * @returns {string}
   */
  getFrequency() {
    return this.getField('frequency');
  }
  
  /**
   * Get term.
   * @returns {number}
   */
  getTerm() {
    return this.getField('term', 0);
  }
  
  /**
   * Get descrip.
   * @returns {string}
   */
  getDescription() {
    return this.getField('descrip');
  }
  
  /**
   * Get n.
   * @returns {number}
   */
  getN() {
    return this.getField('n', 0);
  }
  
  /**
   * Get fixed_dow.
   * @returns {number}
   */
  getFixedDayOfWeek() {
    return this.getField('fixed_dow', 0);
  }
  
  /**
   * Get fixed_dom.
   * @returns {number}
   */
  getFixedDayOfMonth() {
    return this.getField('fixed_dom', 0);
  }
  
  /**
   * Get sub_count.
   * @returns {number}
   */
  getSubscriptionCount() {
    return this.getField('sub_count', 0);
  }
}

/** OrderCustomField data model. */
class OrderCustomField extends Model {
  /**
   * OrderCustomField Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.module)) {
      if (!util.isInstanceOf(this.module, Module) && util.isObject(this.module)) {
        this.module = new Module(this.module);
      } else if (!util.isInstanceOf(this.module, Module)) {
        throw new Error(util.format('Expected Module or an Object but got %s',
          typeof this.module));
      }
    } else {
      this.module = {};
    }
  }

  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get name.
   * @returns {string}
   */
  getName() {
    return this.getField('name');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get searchable.
   * @returns {boolean}
   */
  getSearchable() {
    return this.getField('searchable', false);
  }
  
  /**
   * Get sortable.
   * @returns {boolean}
   */
  getSortable() {
    return this.getField('sortable', false);
  }
  
  /**
   * Get module.
   * @returns {Module|*}
   */
  getModule() {
    return this.getField('module', null);
  }
  
  /**
   * Get choices.
   * @returns {array}
   */
  getChoices() {
    return this.getField('choices', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['module'], Module)) {
      ret['module'] = ret['module'].toObject();
    }

    return ret;
  }
}

/** CustomerPaymentCard data model. */
class CustomerPaymentCard extends Model {
  /**
   * CustomerPaymentCard Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get cust_id.
   * @returns {number}
   */
  getCustomerId() {
    return this.getField('cust_id', 0);
  }
  
  /**
   * Get fname.
   * @returns {string}
   */
  getFirstName() {
    return this.getField('fname');
  }
  
  /**
   * Get lname.
   * @returns {string}
   */
  getLastName() {
    return this.getField('lname');
  }
  
  /**
   * Get exp_month.
   * @returns {number}
   */
  getExpirationMonth() {
    return this.getField('exp_month', 0);
  }
  
  /**
   * Get exp_year.
   * @returns {number}
   */
  getExpirationYear() {
    return this.getField('exp_year', 0);
  }
  
  /**
   * Get lastfour.
   * @returns {string}
   */
  getLastFour() {
    return this.getField('lastfour');
  }
  
  /**
   * Get addr1.
   * @returns {string}
   */
  getAddress1() {
    return this.getField('addr1');
  }
  
  /**
   * Get addr2.
   * @returns {string}
   */
  getAddress2() {
    return this.getField('addr2');
  }
  
  /**
   * Get city.
   * @returns {string}
   */
  getCity() {
    return this.getField('city');
  }
  
  /**
   * Get state.
   * @returns {string}
   */
  getState() {
    return this.getField('state');
  }
  
  /**
   * Get zip.
   * @returns {string}
   */
  getZip() {
    return this.getField('zip');
  }
  
  /**
   * Get cntry.
   * @returns {string}
   */
  getCountry() {
    return this.getField('cntry');
  }
  
  /**
   * Get lastused.
   * @returns {string}
   */
  getLastUsed() {
    return this.getField('lastused');
  }
  
  /**
   * Get token.
   * @returns {string}
   */
  getToken() {
    return this.getField('token');
  }
  
  /**
   * Get type_id.
   * @returns {number}
   */
  getTypeId() {
    return this.getField('type_id', 0);
  }
  
  /**
   * Get refcount.
   * @returns {number}
   */
  getReferenceCount() {
    return this.getField('refcount', 0);
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get mod_code.
   * @returns {string}
   */
  getModuleCode() {
    return this.getField('mod_code');
  }
  
  /**
   * Get meth_code.
   * @returns {string}
   */
  getMethodCode() {
    return this.getField('meth_code');
  }
}

/** OrderProductAttribute data model. */
class OrderProductAttribute extends Model {
  /**
   * OrderProductAttribute Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get template_code.
   * @returns {string}
   */
  getTemplateCode() {
    return this.getField('template_code');
  }
  
  /**
   * Get value.
   * @returns {string}
   */
  getValue() {
    return this.getField('value');
  }
  
  /**
   * Set code.
   * @param {string} code
   * @returns {OrderProductAttribute}
   */
  setCode(code) {
    return this.setField('code', code);
  }

  /**
   * Set template_code.
   * @param {string} templateCode
   * @returns {OrderProductAttribute}
   */
  setTemplateCode(templateCode) {
    return this.setField('template_code', templateCode);
  }

  /**
   * Set value.
   * @param {string} value
   * @returns {OrderProductAttribute}
   */
  setValue(value) {
    return this.setField('value', value);
  }
}

/** OrderProduct data model. */
class OrderProduct extends Model {
  /**
   * OrderProduct Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.attributes) && util.isArray(this.attributes)) {
      for (i = 0, l = this.attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.attributes[i], OrderProductAttribute) && util.isObject(data['attributes'][i])) {
          this.attributes[i] = new OrderProductAttribute(this.attributes[i]);
        } else if (!util.isInstanceOf(this.attributes[i], OrderProductAttribute)) {
          throw new Error(util.format('Expected array of OrderProductAttribute or an array of Objects but got %s',
            typeof this.attributes[i]));
        }
      }
    } else {
      this.attributes = [];
    }
  }

  /**
   * Get status.
   * @returns {number}
   */
  getStatus() {
    return this.getField('status', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get sku.
   * @returns {string}
   */
  getSku() {
    return this.getField('sku');
  }
  
  /**
   * Get tracknum.
   * @returns {string}
   */
  getTrackingNumber() {
    return this.getField('tracknum');
  }
  
  /**
   * Get tracktype.
   * @returns {string}
   */
  getTrackingType() {
    return this.getField('tracktype');
  }
  
  /**
   * Get quantity.
   * @returns {number}
   */
  getQuantity() {
    return this.getField('quantity', 0);
  }
  
  /**
   * Get attributes.
   * @returns {OrderProductAttribute[]}
   */
  getAttributes() {
    return this.getField('attributes', []);
  }
  
  /**
   * Set status.
   * @param {number} status
   * @returns {OrderProduct}
   */
  setStatus(status) {
    return this.setField('status', status);
  }

  /**
   * Set code.
   * @param {string} code
   * @returns {OrderProduct}
   */
  setCode(code) {
    return this.setField('code', code);
  }

  /**
   * Set sku.
   * @param {string} sku
   * @returns {OrderProduct}
   */
  setSku(sku) {
    return this.setField('sku', sku);
  }

  /**
   * Set tracknum.
   * @param {string} trackingNumber
   * @returns {OrderProduct}
   */
  setTrackingNumber(trackingNumber) {
    return this.setField('tracknum', trackingNumber);
  }

  /**
   * Set tracktype.
   * @param {string} trackingType
   * @returns {OrderProduct}
   */
  setTrackingType(trackingType) {
    return this.setField('tracktype', trackingType);
  }

  /**
   * Set quantity.
   * @param {number} quantity
   * @returns {OrderProduct}
   */
  setQuantity(quantity) {
    return this.setField('quantity', quantity);
  }

  /**
   * Set attributes.
   * @param {OrderProductAttribute[]} attributes
   * @throws {Error}
   * @returns {OrderProduct}
   */
  setAttributes(attributes) {
    var i;
    var l;

    if (!util.isArray(attributes)) {
      throw new Error(util.format('Expected an array but got %s', typeof attributes));
    }

    for (i = 0, l = attributes.length; i < l; i++) {
      if (util.isInstanceOf(attributes[i], OrderProductAttribute)) {
          continue;
      } else if (util.isObject(attributes[i])) {
          attributes[i] = new OrderProductAttribute(attributes[i]);
      } else {
        throw new Error(util.format('Expected instance of OrderProductAttribute, Object, or null but got %s at offset %d',
          typeof attributes[i], i));
      }
    }

    return this.setField('attributes', attributes);
  }

  /**
   * Add a OrderProductAttribute.
   * @param {OrderProductAttribute} attribute
   * @returns {OrderProduct}
   */
  addAttribute(attribute) {
    if (!util.isInstanceOf(attribute, OrderProductAttribute)) {
      throw new Error(util.format('Expected instance of OrderProductAttribute but got %s', typeof attribute));
    }

    if (util.isUndefined(this['attributes'])) {
      this['attributes'] = [];
    }

    this['attributes'].push(attribute);

    return this;
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['attributes'])) {
      for (i = 0, l = ret['attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['attributes'][i], OrderProductAttribute)) {
          ret['attributes'][i] = ret['attributes'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** ProductInventorySettings data model. */
class ProductInventorySettings extends Model {
  /**
   * ProductInventorySettings Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('active', false);
  }
  
  /**
   * Get in_short.
   * @returns {string}
   */
  getInStockMessageShort() {
    return this.getField('in_short');
  }
  
  /**
   * Get in_long.
   * @returns {string}
   */
  getInStockMessageLong() {
    return this.getField('in_long');
  }
  
  /**
   * Get low_track.
   * @returns {string}
   */
  getTrackLowStockLevel() {
    return this.getField('low_track');
  }
  
  /**
   * Get low_level.
   * @returns {number}
   */
  getLowStockLevel() {
    return this.getField('low_level', 0);
  }
  
  /**
   * Get low_lvl_d.
   * @returns {boolean}
   */
  getLowStockLevelDefault() {
    return this.getField('low_lvl_d', false);
  }
  
  /**
   * Get low_short.
   * @returns {string}
   */
  getLowStockMessageShort() {
    return this.getField('low_short');
  }
  
  /**
   * Get low_long.
   * @returns {string}
   */
  getLowStockMessageLong() {
    return this.getField('low_long');
  }
  
  /**
   * Get out_track.
   * @returns {string}
   */
  getTrackOutOfStockLevel() {
    return this.getField('out_track');
  }
  
  /**
   * Get out_hide.
   * @returns {string}
   */
  getHideOutOfStock() {
    return this.getField('out_hide');
  }
  
  /**
   * Get out_level.
   * @returns {number}
   */
  getOutOfStockLevel() {
    return this.getField('out_level', 0);
  }
  
  /**
   * Get out_lvl_d.
   * @returns {boolean}
   */
  getOutOfStockLevelDefault() {
    return this.getField('out_lvl_d', false);
  }
  
  /**
   * Get out_short.
   * @returns {string}
   */
  getOutOfStockMessageShort() {
    return this.getField('out_short');
  }
  
  /**
   * Get out_long.
   * @returns {string}
   */
  getOutOfStockMessageLong() {
    return this.getField('out_long');
  }
  
  /**
   * Get ltd_long.
   * @returns {string}
   */
  getLimitedStockMessage() {
    return this.getField('ltd_long');
  }
}

/** ProductVariantPart data model. */
class ProductVariantPart extends Model {
  /**
   * ProductVariantPart Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get product_code.
   * @returns {string}
   */
  getProductCode() {
    return this.getField('product_code');
  }
  
  /**
   * Get product_name.
   * @returns {string}
   */
  getProductName() {
    return this.getField('product_name');
  }
  
  /**
   * Get product_sku.
   * @returns {string}
   */
  getProductSku() {
    return this.getField('product_sku');
  }
  
  /**
   * Get quantity.
   * @returns {number}
   */
  getQuantity() {
    return this.getField('quantity', 0);
  }
  
  /**
   * Get offset.
   * @returns {number}
   */
  getOffset() {
    return this.getField('offset', 0);
  }
}

/** ProductVariantDimension data model. */
class ProductVariantDimension extends Model {
  /**
   * ProductVariantDimension Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get attr_id.
   * @returns {number}
   */
  getAttributeId() {
    return this.getField('attr_id', 0);
  }
  
  /**
   * Get attmpat_id.
   * @returns {number}
   */
  getAttributeTemplateAttributeId() {
    return this.getField('attmpat_id', 0);
  }
  
  /**
   * Get option_id.
   * @returns {number}
   */
  getOptionId() {
    return this.getField('option_id', 0);
  }
  
  /**
   * Get option_code.
   * @returns {string}
   */
  getOptionCode() {
    return this.getField('option_code');
  }
}

/** OrderItemSubscription data model. */
class OrderItemSubscription extends Model {
  /**
   * OrderItemSubscription Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.productsubscriptionterm)) {
      if (!util.isInstanceOf(this.productsubscriptionterm, ProductSubscriptionTerm) && util.isObject(this.productsubscriptionterm)) {
        this.productsubscriptionterm = new ProductSubscriptionTerm(this.productsubscriptionterm);
      } else if (!util.isInstanceOf(this.productsubscriptionterm, ProductSubscriptionTerm)) {
        throw new Error(util.format('Expected ProductSubscriptionTerm or an Object but got %s',
          typeof this.productsubscriptionterm));
      }
    } else {
      this.productsubscriptionterm = {};
    }

    if (!util.isUndefined(this.options) && util.isArray(this.options)) {
      for (i = 0, l = this.options.length; i < l; i++) {
        if (!util.isInstanceOf(this.options[i], SubscriptionOption) && util.isObject(data['options'][i])) {
          this.options[i] = new SubscriptionOption(this.options[i]);
        } else if (!util.isInstanceOf(this.options[i], SubscriptionOption)) {
          throw new Error(util.format('Expected array of SubscriptionOption or an array of Objects but got %s',
            typeof this.options[i]));
        }
      }
    } else {
      this.options = [];
    }
  }

  /**
   * Get method.
   * @returns {string}
   */
  getMethod() {
    return this.getField('method');
  }
  
  /**
   * Get productsubscriptionterm.
   * @returns {ProductSubscriptionTerm|*}
   */
  getProductSubscriptionTerm() {
    return this.getField('productsubscriptionterm', null);
  }
  
  /**
   * Get options.
   * @returns {SubscriptionOption[]}
   */
  getOptions() {
    return this.getField('options', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['productsubscriptionterm'], ProductSubscriptionTerm)) {
      ret['productsubscriptionterm'] = ret['productsubscriptionterm'].toObject();
    }

    if (util.isArray(ret['options'])) {
      for (i = 0, l = ret['options'].length; i < l; i++) {
        if (util.isInstanceOf(ret['options'][i], SubscriptionOption)) {
          ret['options'][i] = ret['options'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** SubscriptionOption data model. */
class SubscriptionOption extends Model {
  /**
   * SubscriptionOption Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get subscrp_id.
   * @returns {number}
   */
  getSubscriptionId() {
    return this.getField('subscrp_id', 0);
  }
  
  /**
   * Get templ_code.
   * @returns {string}
   */
  getTemplateCode() {
    return this.getField('templ_code');
  }
  
  /**
   * Get attr_code.
   * @returns {string}
   */
  getAttributeCode() {
    return this.getField('attr_code');
  }
  
  /**
   * Get value.
   * @returns {string}
   */
  getValue() {
    return this.getField('value');
  }
}

/** ProductInventoryAdjustment data model. */
class ProductInventoryAdjustment extends Model {
  /**
   * ProductInventoryAdjustment Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get product_code.
   * @returns {string}
   */
  getProductCode() {
    return this.getField('product_code');
  }
  
  /**
   * Get product_sku.
   * @returns {string}
   */
  getProductSku() {
    return this.getField('product_sku');
  }
  
  /**
   * Get adjustment.
   * @returns {number}
   */
  getAdjustment() {
    return this.getField('adjustment', 0.00);
  }
  
  /**
   * Set product_id.
   * @param {number} productId
   * @returns {ProductInventoryAdjustment}
   */
  setProductId(productId) {
    return this.setField('product_id', productId);
  }

  /**
   * Set product_code.
   * @param {string} productCode
   * @returns {ProductInventoryAdjustment}
   */
  setProductCode(productCode) {
    return this.setField('product_code', productCode);
  }

  /**
   * Set product_sku.
   * @param {string} productSku
   * @returns {ProductInventoryAdjustment}
   */
  setProductSku(productSku) {
    return this.setField('product_sku', productSku);
  }

  /**
   * Set adjustment.
   * @param {number} adjustment
   * @returns {ProductInventoryAdjustment}
   */
  setAdjustment(adjustment) {
    return this.setField('adjustment', adjustment);
  }
}

/** OrderShipmentUpdate data model. */
class OrderShipmentUpdate extends Model {
  /**
   * OrderShipmentUpdate Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get shpmnt_id.
   * @returns {number}
   */
  getShipmentId() {
    return this.getField('shpmnt_id', 0);
  }
  
  /**
   * Get mark_shipped.
   * @returns {boolean}
   */
  getMarkShipped() {
    return this.getField('mark_shipped', false);
  }
  
  /**
   * Get tracknum.
   * @returns {string}
   */
  getTrackingNumber() {
    return this.getField('tracknum');
  }
  
  /**
   * Get tracktype.
   * @returns {string}
   */
  getTrackingType() {
    return this.getField('tracktype');
  }
  
  /**
   * Get cost.
   * @returns {number}
   */
  getCost() {
    return this.getField('cost', 0.00);
  }
  
  /**
   * Set shpmnt_id.
   * @param {number} shipmentId
   * @returns {OrderShipmentUpdate}
   */
  setShipmentId(shipmentId) {
    return this.setField('shpmnt_id', shipmentId);
  }

  /**
   * Set mark_shipped.
   * @param {boolean} markShipped
   * @returns {OrderShipmentUpdate}
   */
  setMarkShipped(markShipped) {
    return this.setField('mark_shipped', markShipped);
  }

  /**
   * Set tracknum.
   * @param {string} trackingNumber
   * @returns {OrderShipmentUpdate}
   */
  setTrackingNumber(trackingNumber) {
    return this.setField('tracknum', trackingNumber);
  }

  /**
   * Set tracktype.
   * @param {string} trackingType
   * @returns {OrderShipmentUpdate}
   */
  setTrackingType(trackingType) {
    return this.setField('tracktype', trackingType);
  }

  /**
   * Set cost.
   * @param {number} cost
   * @returns {OrderShipmentUpdate}
   */
  setCost(cost) {
    return this.setField('cost', cost);
  }
}

/** ProductVariantLimit data model. */
class ProductVariantLimit extends Model {
  /**
   * ProductVariantLimit Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get attr_id.
   * @returns {number}
   */
  getAttributeId() {
    return this.getField('attr_id', 0);
  }
  
  /**
   * Get attmpat_id.
   * @returns {number}
   */
  getAttributeTemplateId() {
    return this.getField('attmpat_id', 0);
  }
  
  /**
   * Get option_id.
   * @returns {number}
   */
  getOptionId() {
    return this.getField('option_id', 0);
  }
  
  /**
   * Set attr_id.
   * @param {number} attributeId
   * @returns {ProductVariantLimit}
   */
  setAttributeId(attributeId) {
    return this.setField('attr_id', attributeId);
  }

  /**
   * Set attmpat_id.
   * @param {number} attributeTemplateId
   * @returns {ProductVariantLimit}
   */
  setAttributeTemplateId(attributeTemplateId) {
    return this.setField('attmpat_id', attributeTemplateId);
  }

  /**
   * Set option_id.
   * @param {number} optionId
   * @returns {ProductVariantLimit}
   */
  setOptionId(optionId) {
    return this.setField('option_id', optionId);
  }
}

/** ProductVariantExclusion data model. */
class ProductVariantExclusion extends Model {
  /**
   * ProductVariantExclusion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get attr_id.
   * @returns {number}
   */
  getAttributeId() {
    return this.getField('attr_id', 0);
  }
  
  /**
   * Get attmpat_id.
   * @returns {number}
   */
  getAttributeTemplateId() {
    return this.getField('attmpat_id', 0);
  }
  
  /**
   * Get option_id.
   * @returns {number}
   */
  getOptionId() {
    return this.getField('option_id', 0);
  }
  
  /**
   * Set attr_id.
   * @param {number} attributeId
   * @returns {ProductVariantExclusion}
   */
  setAttributeId(attributeId) {
    return this.setField('attr_id', attributeId);
  }

  /**
   * Set attmpat_id.
   * @param {number} attributeTemplateId
   * @returns {ProductVariantExclusion}
   */
  setAttributeTemplateId(attributeTemplateId) {
    return this.setField('attmpat_id', attributeTemplateId);
  }

  /**
   * Set option_id.
   * @param {number} optionId
   * @returns {ProductVariantExclusion}
   */
  setOptionId(optionId) {
    return this.setField('option_id', optionId);
  }
}

/** ProvisionMessage data model. */
class ProvisionMessage extends Model {
  /**
   * ProvisionMessage Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get dtstamp.
   * @returns {string}
   */
  getDateTimeStamp() {
    return this.getField('dtstamp');
  }
  
  /**
   * Get lineno.
   * @returns {number}
   */
  getLineNumber() {
    return this.getField('lineno', 0);
  }
  
  /**
   * Get tag.
   * @returns {string}
   */
  getTag() {
    return this.getField('tag');
  }
  
  /**
   * Get message.
   * @returns {string}
   */
  getMessage() {
    return this.getField('message');
  }
}

/** CustomerAddress data model. */
class CustomerAddress extends Model {
  /**
   * CustomerAddress Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get cust_id.
   * @returns {number}
   */
  getCustomerId() {
    return this.getField('cust_id', 0);
  }
  
  /**
   * Get descrip.
   * @returns {string}
   */
  getDescription() {
    return this.getField('descrip');
  }
  
  /**
   * Get fname.
   * @returns {string}
   */
  getFirstName() {
    return this.getField('fname');
  }
  
  /**
   * Get lname.
   * @returns {string}
   */
  getLastName() {
    return this.getField('lname');
  }
  
  /**
   * Get email.
   * @returns {string}
   */
  getEmail() {
    return this.getField('email');
  }
  
  /**
   * Get comp.
   * @returns {string}
   */
  getCompany() {
    return this.getField('comp');
  }
  
  /**
   * Get phone.
   * @returns {string}
   */
  getPhone() {
    return this.getField('phone');
  }
  
  /**
   * Get fax.
   * @returns {string}
   */
  getFax() {
    return this.getField('fax');
  }
  
  /**
   * Get addr1.
   * @returns {string}
   */
  getAddress1() {
    return this.getField('addr1');
  }
  
  /**
   * Get addr2.
   * @returns {string}
   */
  getAddress2() {
    return this.getField('addr2');
  }
  
  /**
   * Get city.
   * @returns {string}
   */
  getCity() {
    return this.getField('city');
  }
  
  /**
   * Get state.
   * @returns {string}
   */
  getState() {
    return this.getField('state');
  }
  
  /**
   * Get zip.
   * @returns {string}
   */
  getZip() {
    return this.getField('zip');
  }
  
  /**
   * Get cntry.
   * @returns {string}
   */
  getCountry() {
    return this.getField('cntry');
  }
  
  /**
   * Get resdntl.
   * @returns {boolean}
   */
  getResidential() {
    return this.getField('resdntl', false);
  }
}

/** OrderTotal data model. */
class OrderTotal extends Model {
  /**
   * OrderTotal Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get total.
   * @returns {number}
   */
  getTotal() {
    return this.getField('total', 0.00);
  }
  
  /**
   * Get formatted_total.
   * @returns {string}
   */
  getFormattedTotal() {
    return this.getField('formatted_total');
  }
}

/** OrderPaymentTotal data model. */
class OrderPaymentTotal extends Model {
  /**
   * OrderPaymentTotal Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get order_id.
   * @returns {number}
   */
  getOrderId() {
    return this.getField('order_id', 0);
  }
  
  /**
   * Get total_auth.
   * @returns {number}
   */
  getTotalAuthorized() {
    return this.getField('total_auth', 0.00);
  }
  
  /**
   * Get formatted_total_auth.
   * @returns {string}
   */
  getFormattedTotalAuthorized() {
    return this.getField('formatted_total_auth');
  }
  
  /**
   * Get total_capt.
   * @returns {number}
   */
  getTotalCaptured() {
    return this.getField('total_capt', 0.00);
  }
  
  /**
   * Get formatted_total_capt.
   * @returns {string}
   */
  getFormattedTotalCaptured() {
    return this.getField('formatted_total_capt');
  }
  
  /**
   * Get total_rfnd.
   * @returns {number}
   */
  getTotalRefunded() {
    return this.getField('total_rfnd', 0.00);
  }
  
  /**
   * Get formatted_total_rfnd.
   * @returns {string}
   */
  getFormattedTotalRefunded() {
    return this.getField('formatted_total_rfnd');
  }
  
  /**
   * Get net_capt.
   * @returns {number}
   */
  getNetCaptured() {
    return this.getField('net_capt', 0.00);
  }
  
  /**
   * Get formatted_net_capt.
   * @returns {string}
   */
  getFormattedNetCaptured() {
    return this.getField('formatted_net_capt');
  }
}

/** PrintQueue data model. */
class PrintQueue extends Model {
  /**
   * PrintQueue Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get descrip.
   * @returns {string}
   */
  getDescription() {
    return this.getField('descrip');
  }
}

/** PrintQueueJob data model. */
class PrintQueueJob extends Model {
  /**
   * PrintQueueJob Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get queue_id.
   * @returns {number}
   */
  getQueueId() {
    return this.getField('queue_id', 0);
  }
  
  /**
   * Get store_id.
   * @returns {number}
   */
  getStoreId() {
    return this.getField('store_id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get descrip.
   * @returns {string}
   */
  getDescription() {
    return this.getField('descrip');
  }
  
  /**
   * Get job_fmt.
   * @returns {string}
   */
  getJobFormat() {
    return this.getField('job_fmt');
  }
  
  /**
   * Get job_data.
   * @returns {string}
   */
  getJobData() {
    return this.getField('job_data');
  }
  
  /**
   * Get dt_created.
   * @returns {number}
   */
  getDateTimeCreated() {
    return this.getField('dt_created', 0);
  }
  
  /**
   * Get printqueue_descrip.
   * @returns {string}
   */
  getPrintQueueDescription() {
    return this.getField('printqueue_descrip');
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
  
  /**
   * Get store_code.
   * @returns {string}
   */
  getStoreCode() {
    return this.getField('store_code');
  }
  
  /**
   * Get store_name.
   * @returns {string}
   */
  getStoreName() {
    return this.getField('store_name');
  }
}

/** PaymentMethod data model. */
class PaymentMethod extends Model {
  /**
   * PaymentMethod Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.paymentcard)) {
      if (!util.isInstanceOf(this.paymentcard, CustomerPaymentCard) && util.isObject(this.paymentcard)) {
        this.paymentcard = new CustomerPaymentCard(this.paymentcard);
      } else if (!util.isInstanceOf(this.paymentcard, CustomerPaymentCard)) {
        throw new Error(util.format('Expected CustomerPaymentCard or an Object but got %s',
          typeof this.paymentcard));
      }
    } else {
      this.paymentcard = {};
    }

    if (!util.isUndefined(this.orderpaymentcard)) {
      if (!util.isInstanceOf(this.orderpaymentcard, OrderPaymentCard) && util.isObject(this.orderpaymentcard)) {
        this.orderpaymentcard = new OrderPaymentCard(this.orderpaymentcard);
      } else if (!util.isInstanceOf(this.orderpaymentcard, OrderPaymentCard)) {
        throw new Error(util.format('Expected OrderPaymentCard or an Object but got %s',
          typeof this.orderpaymentcard));
      }
    } else {
      this.orderpaymentcard = {};
    }

    if (!util.isUndefined(this.paymentcardtype)) {
      if (!util.isInstanceOf(this.paymentcardtype, PaymentCardType) && util.isObject(this.paymentcardtype)) {
        this.paymentcardtype = new PaymentCardType(this.paymentcardtype);
      } else if (!util.isInstanceOf(this.paymentcardtype, PaymentCardType)) {
        throw new Error(util.format('Expected PaymentCardType or an Object but got %s',
          typeof this.paymentcardtype));
      }
    } else {
      this.paymentcardtype = {};
    }
  }

  /**
   * Get module_id.
   * @returns {number}
   */
  getModuleId() {
    return this.getField('module_id', 0);
  }
  
  /**
   * Get module_api.
   * @returns {number}
   */
  getModuleApi() {
    return this.getField('module_api', 0.00);
  }
  
  /**
   * Get method_code.
   * @returns {string}
   */
  getMethodCode() {
    return this.getField('method_code');
  }
  
  /**
   * Get method_name.
   * @returns {string}
   */
  getMethodName() {
    return this.getField('method_name');
  }
  
  /**
   * Get mivapay.
   * @returns {boolean}
   */
  getMivapay() {
    return this.getField('mivapay', false);
  }
  
  /**
   * Get paymentcard.
   * @returns {CustomerPaymentCard|*}
   */
  getPaymentCard() {
    return this.getField('paymentcard', null);
  }
  
  /**
   * Get orderpaymentcard.
   * @returns {OrderPaymentCard|*}
   */
  getOrderPaymentCard() {
    return this.getField('orderpaymentcard', null);
  }
  
  /**
   * Get paymentcardtype.
   * @returns {PaymentCardType|*}
   */
  getPaymentCardType() {
    return this.getField('paymentcardtype', null);
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['paymentcard'], CustomerPaymentCard)) {
      ret['paymentcard'] = ret['paymentcard'].toObject();
    }

    if (util.isInstanceOf(ret['orderpaymentcard'], OrderPaymentCard)) {
      ret['orderpaymentcard'] = ret['orderpaymentcard'].toObject();
    }

    if (util.isInstanceOf(ret['paymentcardtype'], PaymentCardType)) {
      ret['paymentcardtype'] = ret['paymentcardtype'].toObject();
    }

    return ret;
  }
}

/** PaymentCardType data model. */
class PaymentCardType extends Model {
  /**
   * PaymentCardType Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get prefixes.
   * @returns {string}
   */
  getPrefixes() {
    return this.getField('prefixes');
  }
  
  /**
   * Get lengths.
   * @returns {string}
   */
  getLengths() {
    return this.getField('lengths');
  }
  
  /**
   * Get cvv.
   * @returns {boolean}
   */
  getCvv() {
    return this.getField('cvv', false);
  }
}

/** OrderPaymentAuthorize data model. */
class OrderPaymentAuthorize extends Model {
  /**
   * OrderPaymentAuthorize Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get valid.
   * @returns {boolean}
   */
  getValid() {
    return this.getField('valid', false);
  }
  
  /**
   * Get total_auth.
   * @returns {number}
   */
  getTotalAuthorized() {
    return this.getField('total_auth', 0.00);
  }
  
  /**
   * Get formatted_total_auth.
   * @returns {string}
   */
  getFormattedTotalAuthorized() {
    return this.getField('formatted_total_auth');
  }
  
  /**
   * Get total_capt.
   * @returns {number}
   */
  getTotalCaptured() {
    return this.getField('total_capt', 0.00);
  }
  
  /**
   * Get formatted_total_capt.
   * @returns {string}
   */
  getFormattedTotalCaptured() {
    return this.getField('formatted_total_capt');
  }
  
  /**
   * Get total_rfnd.
   * @returns {number}
   */
  getTotalRefunded() {
    return this.getField('total_rfnd', 0.00);
  }
  
  /**
   * Get formatted_total_rfnd.
   * @returns {string}
   */
  getFormattedTotalRefunded() {
    return this.getField('formatted_total_rfnd');
  }
  
  /**
   * Get net_capt.
   * @returns {number}
   */
  getNetCaptured() {
    return this.getField('net_capt', 0.00);
  }
  
  /**
   * Get formatted_net_capt.
   * @returns {string}
   */
  getFormattedNetCaptured() {
    return this.getField('formatted_net_capt');
  }
}

/** Branch data model. */
class Branch extends Model {
  /**
   * Branch Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get immutable.
   * @returns {boolean}
   */
  getImmutable() {
    return this.getField('immutable', false);
  }
  
  /**
   * Get branchkey.
   * @returns {string}
   */
  getBranchKey() {
    return this.getField('branchkey');
  }
  
  /**
   * Get name.
   * @returns {string}
   */
  getName() {
    return this.getField('name');
  }
  
  /**
   * Get color.
   * @returns {string}
   */
  getColor() {
    return this.getField('color');
  }
  
  /**
   * Get framework.
   * @returns {string}
   */
  getFramework() {
    return this.getField('framework');
  }
  
  /**
   * Get is_primary.
   * @returns {boolean}
   */
  getIsPrimary() {
    return this.getField('is_primary', false);
  }
  
  /**
   * Get is_working.
   * @returns {boolean}
   */
  getIsWorking() {
    return this.getField('is_working', false);
  }
  
  /**
   * Get preview_url.
   * @returns {string}
   */
  getPreviewUrl() {
    return this.getField('preview_url');
  }
}

/** BranchTemplateVersion data model. */
class BranchTemplateVersion extends Model {
  /**
   * BranchTemplateVersion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.settings)) {
      if (!util.isInstanceOf(this.settings, TemplateVersionSettings)) {
        this.settings = new TemplateVersionSettings(this.settings);
      }
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get parent_id.
   * @returns {number}
   */
  getParentId() {
    return this.getField('parent_id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
  
  /**
   * Get user_icon.
   * @returns {string}
   */
  getUserIcon() {
    return this.getField('user_icon');
  }
  
  /**
   * Get item_id.
   * @returns {number}
   */
  getItemId() {
    return this.getField('item_id', 0);
  }
  
  /**
   * Get prop_id.
   * @returns {number}
   */
  getPropertyId() {
    return this.getField('prop_id', 0);
  }
  
  /**
   * Get sync.
   * @returns {boolean}
   */
  getSync() {
    return this.getField('sync', false);
  }
  
  /**
   * Get filename.
   * @returns {string}
   */
  getFilename() {
    return this.getField('filename');
  }
  
  /**
   * Get dtstamp.
   * @returns {number}
   */
  getDateTimeStamp() {
    return this.getField('dtstamp', 0);
  }
  
  /**
   * Get notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('notes');
  }
  
  /**
   * Get source.
   * @returns {string}
   */
  getSource() {
    return this.getField('source');
  }
  
  /**
   * Get settings.
   * @returns {TemplateVersionSettings|*}
   */
  getSettings() {
    return this.getField('settings', null);
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['settings'], TemplateVersionSettings)) {
      ret['settings'] = ret['settings'].toObject();
    }

    return ret;
  }
}

/** TemplateVersionSettings data model. */
class TemplateVersionSettings extends Model {
  /**
   * TemplateVersionSettings Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super({});
    this.data = data;
  }

  /**
   * Set an items value
   * @return {TemplateVersionSettings}
   */
  setItem(item, value) {
    if (!this.data || this.isObject()) {
      this.data[item] = value;
    }

    return this;
  }

  /**
   * Set an items property value
   * @return {TemplateVersionSettings}
   */
  setItemProperty(item, property, value) {
    if (!this.data || this.isObject()) {
      if (!hasItem(item)) {
        setItem(item, {});
      }

      this.data[item][property] = value;
    }

    return this;
  }

  /**
   * Check if the underlying data is a scalar value
   * @return {bool}
   */
  isScalar() {
    return !util.isArray(this.data) && !util.isObject(this.data);
  }

  /**
   * Check if the underlying data is an array
   * @return {bool}
   */
  isArray() {
    return util.isArray(this.data);
  }

  /**
   * Check if the underlying data is an object
   * @return {bool}
   */
  isObject() {
    return util.isObject(this.data);
  }

  /**
   * Check if an item exists
   * @return {bool}
   */
  hasItem(item) {
    if (this.isObject()) {
      if (util.isObject(this.data[item])) {
        return true;
      }
    }

    return false;
  }

  /**
   * Check if and item has a property
   * @return {bool}
   */
  itemHasProperty(item, property) {
    if (this.isObject()) {
      if (util.isObject(this.data[item])) {
        return !util.isNullOrUndefined(this.data[item][property]);
      }
    }

    return false;
  }

  /**
   * Get an items or null if it does not exist
   * @return {*?}
   */
  getItem(item) {
    if (hasItem(item)) {
      return this.data[item];
    }

    return null;
  }

  /**
   * Get an items property, or null if it does not exist
   * @return {*?}
   */
  getItemProperty() {
    if (itemHasProperty(item)) {
      return this.data[item][property];
    }

    return null;
  }

  /**
   * Get the underlying data.
   * @return {*}
   */
  getData() {
    return this.data;
  }

  /**
   * Get the data for the request.
   * @return {Object}
   */
  toObject() {
    return this.getData();
  }

}

/** Changeset data model. */
class Changeset extends Model {
  /**
   * Changeset Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get branch_id.
   * @returns {number}
   */
  getBranchId() {
    return this.getField('branch_id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get dtstamp.
   * @returns {number}
   */
  getDateTimeStamp() {
    return this.getField('dtstamp', 0);
  }
  
  /**
   * Get notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('notes');
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
  
  /**
   * Get user_icon.
   * @returns {string}
   */
  getUserIcon() {
    return this.getField('user_icon');
  }
  
  /**
   * Get tags.
   * @returns {array}
   */
  getTags() {
    return this.getField('tags', []);
  }
  
  /**
   * Get formatted_tags.
   * @returns {string}
   */
  getFormattedTags() {
    return this.getField('formatted_tags');
  }
}

/** TemplateChange data model. */
class TemplateChange extends Model {
  /**
   * TemplateChange Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.Settings)) {
      if (!util.isInstanceOf(this.Settings, TemplateVersionSettings)) {
        this.Settings = new TemplateVersionSettings(this.Settings);
      }
    }
  }

  /**
   * Get Template_ID.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('Template_ID', 0);
  }
  
  /**
   * Get Template_Filename.
   * @returns {string}
   */
  getTemplateFilename() {
    return this.getField('Template_Filename');
  }
  
  /**
   * Get Source.
   * @returns {string}
   */
  getSource() {
    return this.getField('Source');
  }
  
  /**
   * Get Settings.
   * @returns {TemplateVersionSettings|*}
   */
  getSettings() {
    return this.getField('Settings', null);
  }
  
  /**
   * Get Notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('Notes');
  }
  
  /**
   * Set Template_ID.
   * @param {number} templateId
   * @returns {TemplateChange}
   */
  setTemplateId(templateId) {
    return this.setField('Template_ID', templateId);
  }

  /**
   * Set Template_Filename.
   * @param {string} templateFilename
   * @returns {TemplateChange}
   */
  setTemplateFilename(templateFilename) {
    return this.setField('Template_Filename', templateFilename);
  }

  /**
   * Set Source.
   * @param {string} source
   * @returns {TemplateChange}
   */
  setSource(source) {
    return this.setField('Source', source);
  }

  /**
   * Set Settings.
   * @param {TemplateVersionSettings|Object} settings
   * @returns {TemplateChange}
   * @throws {Error}
   */
  setSettings(settings) {
    if (util.isInstanceOf(settings, TemplateVersionSettings) || util.isNull(settings)) {
      return this.setField('Settings', settings);
    } else if (util.isObject(settings)) {
      return this.setField('Settings', new TemplateVersionSettings(settings));
    }

    throw new Error(util.format('Expected instance of TemplateVersionSettings, Object, or null but got %s',
      typeof settings));
  }

  /**
   * Set Notes.
   * @param {string} notes
   * @returns {TemplateChange}
   */
  setNotes(notes) {
    return this.setField('Notes', notes);
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['Settings'], TemplateVersionSettings)) {
      ret['Settings'] = ret['Settings'].toObject();
    }

    return ret;
  }
}

/** ResourceGroupChange data model. */
class ResourceGroupChange extends Model {
  /**
   * ResourceGroupChange Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get ResourceGroup_ID.
   * @returns {number}
   */
  getResourceGroupId() {
    return this.getField('ResourceGroup_ID', 0);
  }
  
  /**
   * Get ResourceGroup_Code.
   * @returns {string}
   */
  getResourceGroupCode() {
    return this.getField('ResourceGroup_Code');
  }
  
  /**
   * Get LinkedCSSResources.
   * @returns {array}
   */
  getLinkedCSSResources() {
    return this.getField('LinkedCSSResources', []);
  }
  
  /**
   * Get LinkedJavaScriptResources.
   * @returns {array}
   */
  getLinkedJavaScriptResources() {
    return this.getField('LinkedJavaScriptResources', []);
  }
  
  /**
   * Set ResourceGroup_ID.
   * @param {number} resourceGroupId
   * @returns {ResourceGroupChange}
   */
  setResourceGroupId(resourceGroupId) {
    return this.setField('ResourceGroup_ID', resourceGroupId);
  }

  /**
   * Set ResourceGroup_Code.
   * @param {string} resourceGroupCode
   * @returns {ResourceGroupChange}
   */
  setResourceGroupCode(resourceGroupCode) {
    return this.setField('ResourceGroup_Code', resourceGroupCode);
  }

  /**
   * Set LinkedCSSResources.
   * @param {Array} linkedCSSResources
   * @returns {ResourceGroupChange}
   */
  setLinkedCSSResources(linkedCSSResources) {
    return this.setField('LinkedCSSResources', linkedCSSResources);
  }

  /**
   * Set LinkedJavaScriptResources.
   * @param {Array} linkedJavaScriptResources
   * @returns {ResourceGroupChange}
   */
  setLinkedJavaScriptResources(linkedJavaScriptResources) {
    return this.setField('LinkedJavaScriptResources', linkedJavaScriptResources);
  }
}

/** CSSResourceChange data model. */
class CSSResourceChange extends Model {
  /**
   * CSSResourceChange Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.Attributes) && util.isArray(this.Attributes)) {
      for (i = 0, l = this.Attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.Attributes[i], CSSResourceVersionAttribute) && util.isObject(data['Attributes'][i])) {
          this.Attributes[i] = new CSSResourceVersionAttribute(this.Attributes[i]);
        } else if (!util.isInstanceOf(this.Attributes[i], CSSResourceVersionAttribute)) {
          throw new Error(util.format('Expected array of CSSResourceVersionAttribute or an array of Objects but got %s',
            typeof this.Attributes[i]));
        }
      }
    } else {
      this.Attributes = [];
    }
  }

  /**
   * Get CSSResource_ID.
   * @returns {number}
   */
  getCSSResourceId() {
    return this.getField('CSSResource_ID', 0);
  }
  
  /**
   * Get CSSResource_Code.
   * @returns {string}
   */
  getCSSResourceCode() {
    return this.getField('CSSResource_Code');
  }
  
  /**
   * Get Type.
   * @returns {string}
   */
  getType() {
    return this.getField('Type');
  }
  
  /**
   * Get Global.
   * @returns {boolean}
   */
  getGlobal() {
    return this.getField('Global', false);
  }
  
  /**
   * Get Active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('Active', false);
  }
  
  /**
   * Get File_Path.
   * @returns {string}
   */
  getFilePath() {
    return this.getField('File_Path');
  }
  
  /**
   * Get Branchless_File_Path.
   * @returns {string}
   */
  getBranchlessFilePath() {
    return this.getField('Branchless_File_Path');
  }
  
  /**
   * Get Source.
   * @returns {string}
   */
  getSource() {
    return this.getField('Source');
  }
  
  /**
   * Get LinkedPages.
   * @returns {array}
   */
  getLinkedPages() {
    return this.getField('LinkedPages', []);
  }
  
  /**
   * Get LinkedResources.
   * @returns {array}
   */
  getLinkedResources() {
    return this.getField('LinkedResources', []);
  }
  
  /**
   * Get Attributes.
   * @returns {CSSResourceVersionAttribute[]}
   */
  getAttributes() {
    return this.getField('Attributes', []);
  }
  
  /**
   * Get Notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('Notes');
  }
  
  /**
   * Set CSSResource_ID.
   * @param {number} CSSResourceId
   * @returns {CSSResourceChange}
   */
  setCSSResourceId(CSSResourceId) {
    return this.setField('CSSResource_ID', CSSResourceId);
  }

  /**
   * Set CSSResource_Code.
   * @param {string} CSSResourceCode
   * @returns {CSSResourceChange}
   */
  setCSSResourceCode(CSSResourceCode) {
    return this.setField('CSSResource_Code', CSSResourceCode);
  }

  /**
   * Set Type.
   * @param {string} type
   * @returns {CSSResourceChange}
   */
  setType(type) {
    return this.setField('Type', type);
  }

  /**
   * Set Global.
   * @param {boolean} global
   * @returns {CSSResourceChange}
   */
  setGlobal(global) {
    return this.setField('Global', global);
  }

  /**
   * Set Active.
   * @param {boolean} active
   * @returns {CSSResourceChange}
   */
  setActive(active) {
    return this.setField('Active', active);
  }

  /**
   * Set File_Path.
   * @param {string} filePath
   * @returns {CSSResourceChange}
   */
  setFilePath(filePath) {
    return this.setField('File_Path', filePath);
  }

  /**
   * Set Branchless_File_Path.
   * @param {string} branchlessFilePath
   * @returns {CSSResourceChange}
   */
  setBranchlessFilePath(branchlessFilePath) {
    return this.setField('Branchless_File_Path', branchlessFilePath);
  }

  /**
   * Set Source.
   * @param {string} source
   * @returns {CSSResourceChange}
   */
  setSource(source) {
    return this.setField('Source', source);
  }

  /**
   * Set LinkedPages.
   * @param {Array} linkedPages
   * @returns {CSSResourceChange}
   */
  setLinkedPages(linkedPages) {
    return this.setField('LinkedPages', linkedPages);
  }

  /**
   * Set LinkedResources.
   * @param {Array} linkedResources
   * @returns {CSSResourceChange}
   */
  setLinkedResources(linkedResources) {
    return this.setField('LinkedResources', linkedResources);
  }

  /**
   * Set Attributes.
   * @param {CSSResourceVersionAttribute[]} attributes
   * @throws {Error}
   * @returns {CSSResourceChange}
   */
  setAttributes(attributes) {
    var i;
    var l;

    if (!util.isArray(attributes)) {
      throw new Error(util.format('Expected an array but got %s', typeof attributes));
    }

    for (i = 0, l = attributes.length; i < l; i++) {
      if (util.isInstanceOf(attributes[i], CSSResourceVersionAttribute)) {
          continue;
      } else if (util.isObject(attributes[i])) {
          attributes[i] = new CSSResourceVersionAttribute(attributes[i]);
      } else {
        throw new Error(util.format('Expected instance of CSSResourceVersionAttribute, Object, or null but got %s at offset %d',
          typeof attributes[i], i));
      }
    }

    return this.setField('Attributes', attributes);
  }

  /**
   * Set Notes.
   * @param {string} notes
   * @returns {CSSResourceChange}
   */
  setNotes(notes) {
    return this.setField('Notes', notes);
  }

  /**
   * Add a CSSResourceVersionAttribute.
   * @param {CSSResourceVersionAttribute} attribute
   * @returns {CSSResourceChange}
   */
  addAttribute(attribute) {
    if (!util.isInstanceOf(attribute, CSSResourceVersionAttribute)) {
      throw new Error(util.format('Expected instance of CSSResourceVersionAttribute but got %s', typeof attribute));
    }

    if (util.isUndefined(this['Attributes'])) {
      this['Attributes'] = [];
    }

    this['Attributes'].push(attribute);

    return this;
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['Attributes'])) {
      for (i = 0, l = ret['Attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['Attributes'][i], CSSResourceVersionAttribute)) {
          ret['Attributes'][i] = ret['Attributes'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** JavaScriptResourceChange data model. */
class JavaScriptResourceChange extends Model {
  /**
   * JavaScriptResourceChange Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.Attributes) && util.isArray(this.Attributes)) {
      for (i = 0, l = this.Attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.Attributes[i], JavaScriptResourceVersionAttribute) && util.isObject(data['Attributes'][i])) {
          this.Attributes[i] = new JavaScriptResourceVersionAttribute(this.Attributes[i]);
        } else if (!util.isInstanceOf(this.Attributes[i], JavaScriptResourceVersionAttribute)) {
          throw new Error(util.format('Expected array of JavaScriptResourceVersionAttribute or an array of Objects but got %s',
            typeof this.Attributes[i]));
        }
      }
    } else {
      this.Attributes = [];
    }
  }

  /**
   * Get JavaScriptResource_ID.
   * @returns {number}
   */
  getJavaScriptResourceId() {
    return this.getField('JavaScriptResource_ID', 0);
  }
  
  /**
   * Get JavaScriptResource_Code.
   * @returns {string}
   */
  getJavaScriptResourceCode() {
    return this.getField('JavaScriptResource_Code');
  }
  
  /**
   * Get Type.
   * @returns {string}
   */
  getType() {
    return this.getField('Type');
  }
  
  /**
   * Get Global.
   * @returns {boolean}
   */
  getGlobal() {
    return this.getField('Global', false);
  }
  
  /**
   * Get Active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('Active', false);
  }
  
  /**
   * Get File_Path.
   * @returns {string}
   */
  getFilePath() {
    return this.getField('File_Path');
  }
  
  /**
   * Get Branchless_File_Path.
   * @returns {string}
   */
  getBranchlessFilePath() {
    return this.getField('Branchless_File_Path');
  }
  
  /**
   * Get Source.
   * @returns {string}
   */
  getSource() {
    return this.getField('Source');
  }
  
  /**
   * Get LinkedPages.
   * @returns {array}
   */
  getLinkedPages() {
    return this.getField('LinkedPages', []);
  }
  
  /**
   * Get LinkedResources.
   * @returns {array}
   */
  getLinkedResources() {
    return this.getField('LinkedResources', []);
  }
  
  /**
   * Get Attributes.
   * @returns {JavaScriptResourceVersionAttribute[]}
   */
  getAttributes() {
    return this.getField('Attributes', []);
  }
  
  /**
   * Get Notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('Notes');
  }
  
  /**
   * Set JavaScriptResource_ID.
   * @param {number} javaScriptResourceId
   * @returns {JavaScriptResourceChange}
   */
  setJavaScriptResourceId(javaScriptResourceId) {
    return this.setField('JavaScriptResource_ID', javaScriptResourceId);
  }

  /**
   * Set JavaScriptResource_Code.
   * @param {string} javaScriptResourceCode
   * @returns {JavaScriptResourceChange}
   */
  setJavaScriptResourceCode(javaScriptResourceCode) {
    return this.setField('JavaScriptResource_Code', javaScriptResourceCode);
  }

  /**
   * Set Type.
   * @param {string} type
   * @returns {JavaScriptResourceChange}
   */
  setType(type) {
    return this.setField('Type', type);
  }

  /**
   * Set Global.
   * @param {boolean} global
   * @returns {JavaScriptResourceChange}
   */
  setGlobal(global) {
    return this.setField('Global', global);
  }

  /**
   * Set Active.
   * @param {boolean} active
   * @returns {JavaScriptResourceChange}
   */
  setActive(active) {
    return this.setField('Active', active);
  }

  /**
   * Set File_Path.
   * @param {string} filePath
   * @returns {JavaScriptResourceChange}
   */
  setFilePath(filePath) {
    return this.setField('File_Path', filePath);
  }

  /**
   * Set Branchless_File_Path.
   * @param {string} branchlessFilePath
   * @returns {JavaScriptResourceChange}
   */
  setBranchlessFilePath(branchlessFilePath) {
    return this.setField('Branchless_File_Path', branchlessFilePath);
  }

  /**
   * Set Source.
   * @param {string} source
   * @returns {JavaScriptResourceChange}
   */
  setSource(source) {
    return this.setField('Source', source);
  }

  /**
   * Set LinkedPages.
   * @param {Array} linkedPages
   * @returns {JavaScriptResourceChange}
   */
  setLinkedPages(linkedPages) {
    return this.setField('LinkedPages', linkedPages);
  }

  /**
   * Set LinkedResources.
   * @param {Array} linkedResources
   * @returns {JavaScriptResourceChange}
   */
  setLinkedResources(linkedResources) {
    return this.setField('LinkedResources', linkedResources);
  }

  /**
   * Set Attributes.
   * @param {JavaScriptResourceVersionAttribute[]} attributes
   * @throws {Error}
   * @returns {JavaScriptResourceChange}
   */
  setAttributes(attributes) {
    var i;
    var l;

    if (!util.isArray(attributes)) {
      throw new Error(util.format('Expected an array but got %s', typeof attributes));
    }

    for (i = 0, l = attributes.length; i < l; i++) {
      if (util.isInstanceOf(attributes[i], JavaScriptResourceVersionAttribute)) {
          continue;
      } else if (util.isObject(attributes[i])) {
          attributes[i] = new JavaScriptResourceVersionAttribute(attributes[i]);
      } else {
        throw new Error(util.format('Expected instance of JavaScriptResourceVersionAttribute, Object, or null but got %s at offset %d',
          typeof attributes[i], i));
      }
    }

    return this.setField('Attributes', attributes);
  }

  /**
   * Set Notes.
   * @param {string} notes
   * @returns {JavaScriptResourceChange}
   */
  setNotes(notes) {
    return this.setField('Notes', notes);
  }

  /**
   * Add a JavaScriptResourceVersionAttribute.
   * @param {JavaScriptResourceVersionAttribute} attribute
   * @returns {JavaScriptResourceChange}
   */
  addAttribute(attribute) {
    if (!util.isInstanceOf(attribute, JavaScriptResourceVersionAttribute)) {
      throw new Error(util.format('Expected instance of JavaScriptResourceVersionAttribute but got %s', typeof attribute));
    }

    if (util.isUndefined(this['Attributes'])) {
      this['Attributes'] = [];
    }

    this['Attributes'].push(attribute);

    return this;
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['Attributes'])) {
      for (i = 0, l = ret['Attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['Attributes'][i], JavaScriptResourceVersionAttribute)) {
          ret['Attributes'][i] = ret['Attributes'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** ChangesetChange data model. */
class ChangesetChange extends Model {
  /**
   * ChangesetChange Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get item_type.
   * @returns {string}
   */
  getItemType() {
    return this.getField('item_type');
  }
  
  /**
   * Get item_id.
   * @returns {number}
   */
  getItemId() {
    return this.getField('item_id', 0);
  }
  
  /**
   * Get item_version_id.
   * @returns {number}
   */
  getItemVersionId() {
    return this.getField('item_version_id', 0);
  }
  
  /**
   * Get item_identifier.
   * @returns {string}
   */
  getItemIdentifier() {
    return this.getField('item_identifier');
  }
}

/** PropertyChange data model. */
class PropertyChange extends Model {
  /**
   * PropertyChange Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.Settings)) {
      if (!util.isInstanceOf(this.Settings, TemplateVersionSettings)) {
        this.Settings = new TemplateVersionSettings(this.Settings);
      }
    }
  }

  /**
   * Get Property_ID.
   * @returns {number}
   */
  getPropertyId() {
    return this.getField('Property_ID', 0);
  }
  
  /**
   * Get Property_Type.
   * @returns {string}
   */
  getPropertyType() {
    return this.getField('Property_Type');
  }
  
  /**
   * Get Property_Code.
   * @returns {string}
   */
  getPropertyCode() {
    return this.getField('Property_Code');
  }
  
  /**
   * Get Product_ID.
   * @returns {number}
   */
  getProductId() {
    return this.getField('Product_ID', 0);
  }
  
  /**
   * Get Product_Code.
   * @returns {string}
   */
  getProductCode() {
    return this.getField('Product_Code');
  }
  
  /**
   * Get Edit_Product.
   * @returns {string}
   */
  getEditProduct() {
    return this.getField('Edit_Product');
  }
  
  /**
   * Get Category_ID.
   * @returns {number}
   */
  getCategoryId() {
    return this.getField('Category_ID', 0);
  }
  
  /**
   * Get Category_Code.
   * @returns {string}
   */
  getCategoryCode() {
    return this.getField('Category_Code');
  }
  
  /**
   * Get Edit_Category.
   * @returns {string}
   */
  getEditCategory() {
    return this.getField('Edit_Category');
  }
  
  /**
   * Get Source.
   * @returns {string}
   */
  getSource() {
    return this.getField('Source');
  }
  
  /**
   * Get Settings.
   * @returns {TemplateVersionSettings|*}
   */
  getSettings() {
    return this.getField('Settings', null);
  }
  
  /**
   * Get Notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('Notes');
  }
  
  /**
   * Set Property_ID.
   * @param {number} propertyId
   * @returns {PropertyChange}
   */
  setPropertyId(propertyId) {
    return this.setField('Property_ID', propertyId);
  }

  /**
   * Set Property_Type.
   * @param {string} propertyType
   * @returns {PropertyChange}
   */
  setPropertyType(propertyType) {
    return this.setField('Property_Type', propertyType);
  }

  /**
   * Set Property_Code.
   * @param {string} propertyCode
   * @returns {PropertyChange}
   */
  setPropertyCode(propertyCode) {
    return this.setField('Property_Code', propertyCode);
  }

  /**
   * Set Product_ID.
   * @param {number} productId
   * @returns {PropertyChange}
   */
  setProductId(productId) {
    return this.setField('Product_ID', productId);
  }

  /**
   * Set Product_Code.
   * @param {string} productCode
   * @returns {PropertyChange}
   */
  setProductCode(productCode) {
    return this.setField('Product_Code', productCode);
  }

  /**
   * Set Edit_Product.
   * @param {string} editProduct
   * @returns {PropertyChange}
   */
  setEditProduct(editProduct) {
    return this.setField('Edit_Product', editProduct);
  }

  /**
   * Set Category_ID.
   * @param {number} categoryId
   * @returns {PropertyChange}
   */
  setCategoryId(categoryId) {
    return this.setField('Category_ID', categoryId);
  }

  /**
   * Set Category_Code.
   * @param {string} categoryCode
   * @returns {PropertyChange}
   */
  setCategoryCode(categoryCode) {
    return this.setField('Category_Code', categoryCode);
  }

  /**
   * Set Edit_Category.
   * @param {string} editCategory
   * @returns {PropertyChange}
   */
  setEditCategory(editCategory) {
    return this.setField('Edit_Category', editCategory);
  }

  /**
   * Set Source.
   * @param {string} source
   * @returns {PropertyChange}
   */
  setSource(source) {
    return this.setField('Source', source);
  }

  /**
   * Set Settings.
   * @param {TemplateVersionSettings|Object} settings
   * @returns {PropertyChange}
   * @throws {Error}
   */
  setSettings(settings) {
    if (util.isInstanceOf(settings, TemplateVersionSettings) || util.isNull(settings)) {
      return this.setField('Settings', settings);
    } else if (util.isObject(settings)) {
      return this.setField('Settings', new TemplateVersionSettings(settings));
    }

    throw new Error(util.format('Expected instance of TemplateVersionSettings, Object, or null but got %s',
      typeof settings));
  }

  /**
   * Set Notes.
   * @param {string} notes
   * @returns {PropertyChange}
   */
  setNotes(notes) {
    return this.setField('Notes', notes);
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['Settings'], TemplateVersionSettings)) {
      ret['Settings'] = ret['Settings'].toObject();
    }

    return ret;
  }
}

/** ChangesetTemplateVersion data model. */
class ChangesetTemplateVersion extends Model {
  /**
   * ChangesetTemplateVersion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.settings)) {
      if (!util.isInstanceOf(this.settings, TemplateVersionSettings)) {
        this.settings = new TemplateVersionSettings(this.settings);
      }
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get parent_id.
   * @returns {number}
   */
  getParentId() {
    return this.getField('parent_id', 0);
  }
  
  /**
   * Get item_id.
   * @returns {number}
   */
  getItemId() {
    return this.getField('item_id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
  
  /**
   * Get user_icon.
   * @returns {string}
   */
  getUserIcon() {
    return this.getField('user_icon');
  }
  
  /**
   * Get prop_id.
   * @returns {number}
   */
  getPropertyId() {
    return this.getField('prop_id', 0);
  }
  
  /**
   * Get sync.
   * @returns {boolean}
   */
  getSync() {
    return this.getField('sync', false);
  }
  
  /**
   * Get filename.
   * @returns {string}
   */
  getFilename() {
    return this.getField('filename');
  }
  
  /**
   * Get dtstamp.
   * @returns {number}
   */
  getDateTimeStamp() {
    return this.getField('dtstamp', 0);
  }
  
  /**
   * Get notes.
   * @returns {string}
   */
  getNotes() {
    return this.getField('notes');
  }
  
  /**
   * Get source.
   * @returns {string}
   */
  getSource() {
    return this.getField('source');
  }
  
  /**
   * Get settings.
   * @returns {TemplateVersionSettings|*}
   */
  getSettings() {
    return this.getField('settings', null);
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['settings'], TemplateVersionSettings)) {
      ret['settings'] = ret['settings'].toObject();
    }

    return ret;
  }
}

/** CSSResourceVersion data model. */
class CSSResourceVersion extends Model {
  /**
   * CSSResourceVersion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.attributes) && util.isArray(this.attributes)) {
      for (i = 0, l = this.attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.attributes[i], CSSResourceVersionAttribute) && util.isObject(data['attributes'][i])) {
          this.attributes[i] = new CSSResourceVersionAttribute(this.attributes[i]);
        } else if (!util.isInstanceOf(this.attributes[i], CSSResourceVersionAttribute)) {
          throw new Error(util.format('Expected array of CSSResourceVersionAttribute or an array of Objects but got %s',
            typeof this.attributes[i]));
        }
      }
    } else {
      this.attributes = [];
    }

    if (!util.isUndefined(this.linkedpages) && util.isArray(this.linkedpages)) {
      for (i = 0, l = this.linkedpages.length; i < l; i++) {
        if (!util.isInstanceOf(this.linkedpages[i], Page) && util.isObject(data['linkedpages'][i])) {
          this.linkedpages[i] = new Page(this.linkedpages[i]);
        } else if (!util.isInstanceOf(this.linkedpages[i], Page)) {
          throw new Error(util.format('Expected array of Page or an array of Objects but got %s',
            typeof this.linkedpages[i]));
        }
      }
    } else {
      this.linkedpages = [];
    }

    if (!util.isUndefined(this.linkedresources) && util.isArray(this.linkedresources)) {
      for (i = 0, l = this.linkedresources.length; i < l; i++) {
        if (!util.isInstanceOf(this.linkedresources[i], CSSResource) && util.isObject(data['linkedresources'][i])) {
          this.linkedresources[i] = new CSSResource(this.linkedresources[i]);
        } else if (!util.isInstanceOf(this.linkedresources[i], CSSResource)) {
          throw new Error(util.format('Expected array of CSSResource or an array of Objects but got %s',
            typeof this.linkedresources[i]));
        }
      }
    } else {
      this.linkedresources = [];
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get res_id.
   * @returns {number}
   */
  getResourceId() {
    return this.getField('res_id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get is_global.
   * @returns {boolean}
   */
  getIsGlobal() {
    return this.getField('is_global', false);
  }
  
  /**
   * Get active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('active', false);
  }
  
  /**
   * Get file.
   * @returns {string}
   */
  getFile() {
    return this.getField('file');
  }
  
  /**
   * Get branchless_file.
   * @returns {string}
   */
  getBranchlessFile() {
    return this.getField('branchless_file');
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
  
  /**
   * Get user_icon.
   * @returns {string}
   */
  getUserIcon() {
    return this.getField('user_icon');
  }
  
  /**
   * Get source_user_id.
   * @returns {number}
   */
  getSourceUserId() {
    return this.getField('source_user_id', 0);
  }
  
  /**
   * Get source_user_name.
   * @returns {string}
   */
  getSourceUserName() {
    return this.getField('source_user_name');
  }
  
  /**
   * Get source_user_icon.
   * @returns {string}
   */
  getSourceUserIcon() {
    return this.getField('source_user_icon');
  }
  
  /**
   * Get source.
   * @returns {string}
   */
  getSource() {
    return this.getField('source');
  }
  
  /**
   * Get attributes.
   * @returns {CSSResourceVersionAttribute[]}
   */
  getAttributes() {
    return this.getField('attributes', []);
  }
  
  /**
   * Get linkedpages.
   * @returns {Page[]}
   */
  getLinkedPages() {
    return this.getField('linkedpages', []);
  }
  
  /**
   * Get linkedresources.
   * @returns {CSSResource[]}
   */
  getLinkedResources() {
    return this.getField('linkedresources', []);
  }
  
  /**
   * Get source_notes.
   * @returns {string}
   */
  getSourceNotes() {
    return this.getField('source_notes');
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['attributes'])) {
      for (i = 0, l = ret['attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['attributes'][i], CSSResourceVersionAttribute)) {
          ret['attributes'][i] = ret['attributes'][i].toObject();
        }
      }
    }

    if (util.isArray(ret['linkedpages'])) {
      for (i = 0, l = ret['linkedpages'].length; i < l; i++) {
        if (util.isInstanceOf(ret['linkedpages'][i], Page)) {
          ret['linkedpages'][i] = ret['linkedpages'][i].toObject();
        }
      }
    }

    if (util.isArray(ret['linkedresources'])) {
      for (i = 0, l = ret['linkedresources'].length; i < l; i++) {
        if (util.isInstanceOf(ret['linkedresources'][i], CSSResource)) {
          ret['linkedresources'][i] = ret['linkedresources'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** CSSResource data model. */
class CSSResource extends Model {
  /**
   * CSSResource Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.attributes) && util.isArray(this.attributes)) {
      for (i = 0, l = this.attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.attributes[i], CSSResourceAttribute) && util.isObject(data['attributes'][i])) {
          this.attributes[i] = new CSSResourceAttribute(this.attributes[i]);
        } else if (!util.isInstanceOf(this.attributes[i], CSSResourceAttribute)) {
          throw new Error(util.format('Expected array of CSSResourceAttribute or an array of Objects but got %s',
            typeof this.attributes[i]));
        }
      }
    } else {
      this.attributes = [];
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get is_global.
   * @returns {boolean}
   */
  getIsGlobal() {
    return this.getField('is_global', false);
  }
  
  /**
   * Get active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('active', false);
  }
  
  /**
   * Get file.
   * @returns {number}
   */
  getFile() {
    return this.getField('file', 0);
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get attributes.
   * @returns {CSSResourceAttribute[]}
   */
  getAttributes() {
    return this.getField('attributes', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['attributes'])) {
      for (i = 0, l = ret['attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['attributes'][i], CSSResourceAttribute)) {
          ret['attributes'][i] = ret['attributes'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** Page data model. */
class Page extends Model {
  /**
   * Page Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get secure.
   * @returns {boolean}
   */
  getSecure() {
    return this.getField('secure', false);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get name.
   * @returns {string}
   */
  getName() {
    return this.getField('name');
  }
  
  /**
   * Get title.
   * @returns {string}
   */
  getTitle() {
    return this.getField('title');
  }
  
  /**
   * Get ui_id.
   * @returns {number}
   */
  getUiId() {
    return this.getField('ui_id', 0);
  }
}

/** JavaScriptResourceVersion data model. */
class JavaScriptResourceVersion extends Model {
  /**
   * JavaScriptResourceVersion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.attributes) && util.isArray(this.attributes)) {
      for (i = 0, l = this.attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.attributes[i], JavaScriptResourceVersionAttribute) && util.isObject(data['attributes'][i])) {
          this.attributes[i] = new JavaScriptResourceVersionAttribute(this.attributes[i]);
        } else if (!util.isInstanceOf(this.attributes[i], JavaScriptResourceVersionAttribute)) {
          throw new Error(util.format('Expected array of JavaScriptResourceVersionAttribute or an array of Objects but got %s',
            typeof this.attributes[i]));
        }
      }
    } else {
      this.attributes = [];
    }

    if (!util.isUndefined(this.linkedpages) && util.isArray(this.linkedpages)) {
      for (i = 0, l = this.linkedpages.length; i < l; i++) {
        if (!util.isInstanceOf(this.linkedpages[i], Page) && util.isObject(data['linkedpages'][i])) {
          this.linkedpages[i] = new Page(this.linkedpages[i]);
        } else if (!util.isInstanceOf(this.linkedpages[i], Page)) {
          throw new Error(util.format('Expected array of Page or an array of Objects but got %s',
            typeof this.linkedpages[i]));
        }
      }
    } else {
      this.linkedpages = [];
    }

    if (!util.isUndefined(this.linkedresources) && util.isArray(this.linkedresources)) {
      for (i = 0, l = this.linkedresources.length; i < l; i++) {
        if (!util.isInstanceOf(this.linkedresources[i], JavaScriptResource) && util.isObject(data['linkedresources'][i])) {
          this.linkedresources[i] = new JavaScriptResource(this.linkedresources[i]);
        } else if (!util.isInstanceOf(this.linkedresources[i], JavaScriptResource)) {
          throw new Error(util.format('Expected array of JavaScriptResource or an array of Objects but got %s',
            typeof this.linkedresources[i]));
        }
      }
    } else {
      this.linkedresources = [];
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get res_id.
   * @returns {number}
   */
  getResourceId() {
    return this.getField('res_id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get is_global.
   * @returns {boolean}
   */
  getIsGlobal() {
    return this.getField('is_global', false);
  }
  
  /**
   * Get active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('active', false);
  }
  
  /**
   * Get file.
   * @returns {string}
   */
  getFile() {
    return this.getField('file');
  }
  
  /**
   * Get branchless_file.
   * @returns {string}
   */
  getBranchlessFile() {
    return this.getField('branchless_file');
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
  
  /**
   * Get user_icon.
   * @returns {string}
   */
  getUserIcon() {
    return this.getField('user_icon');
  }
  
  /**
   * Get source_user_id.
   * @returns {number}
   */
  getSourceUserId() {
    return this.getField('source_user_id', 0);
  }
  
  /**
   * Get source_user_name.
   * @returns {string}
   */
  getSourceUserName() {
    return this.getField('source_user_name');
  }
  
  /**
   * Get source_user_icon.
   * @returns {string}
   */
  getSourceUserIcon() {
    return this.getField('source_user_icon');
  }
  
  /**
   * Get source.
   * @returns {string}
   */
  getSource() {
    return this.getField('source');
  }
  
  /**
   * Get attributes.
   * @returns {JavaScriptResourceVersionAttribute[]}
   */
  getAttributes() {
    return this.getField('attributes', []);
  }
  
  /**
   * Get linkedpages.
   * @returns {Page[]}
   */
  getLinkedPages() {
    return this.getField('linkedpages', []);
  }
  
  /**
   * Get linkedresources.
   * @returns {JavaScriptResource[]}
   */
  getLinkedResources() {
    return this.getField('linkedresources', []);
  }
  
  /**
   * Get source_notes.
   * @returns {string}
   */
  getSourceNotes() {
    return this.getField('source_notes');
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['attributes'])) {
      for (i = 0, l = ret['attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['attributes'][i], JavaScriptResourceVersionAttribute)) {
          ret['attributes'][i] = ret['attributes'][i].toObject();
        }
      }
    }

    if (util.isArray(ret['linkedpages'])) {
      for (i = 0, l = ret['linkedpages'].length; i < l; i++) {
        if (util.isInstanceOf(ret['linkedpages'][i], Page)) {
          ret['linkedpages'][i] = ret['linkedpages'][i].toObject();
        }
      }
    }

    if (util.isArray(ret['linkedresources'])) {
      for (i = 0, l = ret['linkedresources'].length; i < l; i++) {
        if (util.isInstanceOf(ret['linkedresources'][i], JavaScriptResource)) {
          ret['linkedresources'][i] = ret['linkedresources'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** JavaScriptResource data model. */
class JavaScriptResource extends Model {
  /**
   * JavaScriptResource Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.attributes) && util.isArray(this.attributes)) {
      for (i = 0, l = this.attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.attributes[i], JavaScriptResourceAttribute) && util.isObject(data['attributes'][i])) {
          this.attributes[i] = new JavaScriptResourceAttribute(this.attributes[i]);
        } else if (!util.isInstanceOf(this.attributes[i], JavaScriptResourceAttribute)) {
          throw new Error(util.format('Expected array of JavaScriptResourceAttribute or an array of Objects but got %s',
            typeof this.attributes[i]));
        }
      }
    } else {
      this.attributes = [];
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get is_global.
   * @returns {boolean}
   */
  getIsGlobal() {
    return this.getField('is_global', false);
  }
  
  /**
   * Get active.
   * @returns {boolean}
   */
  getActive() {
    return this.getField('active', false);
  }
  
  /**
   * Get file.
   * @returns {number}
   */
  getFile() {
    return this.getField('file', 0);
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get attributes.
   * @returns {JavaScriptResourceAttribute[]}
   */
  getAttributes() {
    return this.getField('attributes', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['attributes'])) {
      for (i = 0, l = ret['attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['attributes'][i], JavaScriptResourceAttribute)) {
          ret['attributes'][i] = ret['attributes'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** ResourceAttribute data model. */
class ResourceAttribute extends Model {
  /**
   * ResourceAttribute Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get name.
   * @returns {string}
   */
  getName() {
    return this.getField('name');
  }
  
  /**
   * Get value.
   * @returns {string}
   */
  getValue() {
    return this.getField('value');
  }
  
  /**
   * Set name.
   * @param {string} name
   * @returns {ResourceAttribute}
   */
  setName(name) {
    return this.setField('name', name);
  }

  /**
   * Set value.
   * @param {string} value
   * @returns {ResourceAttribute}
   */
  setValue(value) {
    return this.setField('value', value);
  }
}

/** CustomerCreditHistory data model. */
class CustomerCreditHistory extends Model {
  /**
   * CustomerCreditHistory Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get user_id.
   * @returns {number}
   */
  getUserId() {
    return this.getField('user_id', 0);
  }
  
  /**
   * Get cust_id.
   * @returns {number}
   */
  getCustomerId() {
    return this.getField('cust_id', 0);
  }
  
  /**
   * Get order_id.
   * @returns {number}
   */
  getOrderId() {
    return this.getField('order_id', 0);
  }
  
  /**
   * Get txref.
   * @returns {string}
   */
  getTransactionReference() {
    return this.getField('txref');
  }
  
  /**
   * Get descrip.
   * @returns {string}
   */
  getDescription() {
    return this.getField('descrip');
  }
  
  /**
   * Get amount.
   * @returns {number}
   */
  getAmount() {
    return this.getField('amount', 0.00);
  }
  
  /**
   * Get dtstamp.
   * @returns {number}
   */
  getDateTimeStamp() {
    return this.getField('dtstamp', 0);
  }
  
  /**
   * Get user_name.
   * @returns {string}
   */
  getUserName() {
    return this.getField('user_name');
  }
}

/** ORDER_RETURN_STATUS constants. */
/** @ignore */
const ORDER_RETURN_STATUS_ISSUED = 500;
/** @ignore */
const ORDER_RETURN_STATUS_RECEIVED = 600;

/** OrderReturn data model. */
class OrderReturn extends Model {
  /**
   * OrderReturn Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Constant ORDER_RETURN_STATUS_ISSUED
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_RETURN_STATUS_ISSUED() {
    return ORDER_RETURN_STATUS_ISSUED;
  }

  /**
   * Constant ORDER_RETURN_STATUS_RECEIVED
   * @returns {number}
   * @const
   * @static
   */
  static get ORDER_RETURN_STATUS_RECEIVED() {
    return ORDER_RETURN_STATUS_RECEIVED;
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get order_id.
   * @returns {number}
   */
  getOrderId() {
    return this.getField('order_id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get status.
   * @returns {number}
   */
  getStatus() {
    return this.getField('status', 0);
  }
  
  /**
   * Get dt_issued.
   * @returns {number}
   */
  getDateTimeIssued() {
    return this.getField('dt_issued', 0);
  }
  
  /**
   * Get dt_recvd.
   * @returns {number}
   */
  getDateTimeReceived() {
    return this.getField('dt_recvd', 0);
  }
}

/** ReceivedReturn data model. */
class ReceivedReturn extends Model {
  /**
   * ReceivedReturn Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get return_id.
   * @returns {number}
   */
  getReturnId() {
    return this.getField('return_id', 0);
  }
  
  /**
   * Get adjust_inventory.
   * @returns {number}
   */
  getAdjustInventory() {
    return this.getField('adjust_inventory', 0);
  }
  
  /**
   * Set return_id.
   * @param {number} returnId
   * @returns {ReceivedReturn}
   */
  setReturnId(returnId) {
    return this.setField('return_id', returnId);
  }

  /**
   * Set adjust_inventory.
   * @param {number} adjustInventory
   * @returns {ReceivedReturn}
   */
  setAdjustInventory(adjustInventory) {
    return this.setField('adjust_inventory', adjustInventory);
  }
}

/** PropertyVersion data model. */
class PropertyVersion extends Model {
  /**
   * PropertyVersion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);

    if (!util.isUndefined(this.settings)) {
      if (!util.isInstanceOf(this.settings, TemplateVersionSettings)) {
        this.settings = new TemplateVersionSettings(this.settings);
      }
    }

    if (!util.isUndefined(this.product)) {
      if (!util.isInstanceOf(this.product, Product) && util.isObject(this.product)) {
        this.product = new Product(this.product);
      } else if (!util.isInstanceOf(this.product, Product)) {
        throw new Error(util.format('Expected Product or an Object but got %s',
          typeof this.product));
      }
    } else {
      this.product = {};
    }

    if (!util.isUndefined(this.category)) {
      if (!util.isInstanceOf(this.category, Category) && util.isObject(this.category)) {
        this.category = new Category(this.category);
      } else if (!util.isInstanceOf(this.category, Category)) {
        throw new Error(util.format('Expected Category or an Object but got %s',
          typeof this.category));
      }
    } else {
      this.category = {};
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get prop_id.
   * @returns {number}
   */
  getPropertyId() {
    return this.getField('prop_id', 0);
  }
  
  /**
   * Get version_id.
   * @returns {number}
   */
  getVersionId() {
    return this.getField('version_id', 0);
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get cat_id.
   * @returns {number}
   */
  getCategoryId() {
    return this.getField('cat_id', 0);
  }
  
  /**
   * Get version_user_id.
   * @returns {number}
   */
  getVersionUserId() {
    return this.getField('version_user_id', 0);
  }
  
  /**
   * Get version_user_name.
   * @returns {string}
   */
  getVersionUserName() {
    return this.getField('version_user_name');
  }
  
  /**
   * Get version_user_icon.
   * @returns {string}
   */
  getVersionUserIcon() {
    return this.getField('version_user_icon');
  }
  
  /**
   * Get source_user_id.
   * @returns {number}
   */
  getSourceUserId() {
    return this.getField('source_user_id', 0);
  }
  
  /**
   * Get source_user_name.
   * @returns {string}
   */
  getSourceUserName() {
    return this.getField('source_user_name');
  }
  
  /**
   * Get source_user_icon.
   * @returns {string}
   */
  getSourceUserIcon() {
    return this.getField('source_user_icon');
  }
  
  /**
   * Get templ_id.
   * @returns {number}
   */
  getTemplateId() {
    return this.getField('templ_id', 0);
  }
  
  /**
   * Get settings.
   * @returns {TemplateVersionSettings|*}
   */
  getSettings() {
    return this.getField('settings', null);
  }
  
  /**
   * Get product.
   * @returns {Product|*}
   */
  getProduct() {
    return this.getField('product', null);
  }
  
  /**
   * Get category.
   * @returns {Category|*}
   */
  getCategory() {
    return this.getField('category', null);
  }
  
  /**
   * Get source.
   * @returns {string}
   */
  getSource() {
    return this.getField('source');
  }
  
  /**
   * Get sync.
   * @returns {boolean}
   */
  getSync() {
    return this.getField('sync', false);
  }
  
  /**
   * Get source_notes.
   * @returns {string}
   */
  getSourceNotes() {
    return this.getField('source_notes');
  }
  
  /**
   * @override
   */
  toObject() {
    var ret = Object.assign(this);

    if (util.isInstanceOf(ret['settings'], TemplateVersionSettings)) {
      ret['settings'] = ret['settings'].toObject();
    }

    if (util.isInstanceOf(ret['product'], Product)) {
      ret['product'] = ret['product'].toObject();
    }

    if (util.isInstanceOf(ret['category'], Category)) {
      ret['category'] = ret['category'].toObject();
    }

    return ret;
  }
}

/** ResourceGroup data model. */
class ResourceGroup extends Model {
  /**
   * ResourceGroup Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.linkedcssresources) && util.isArray(this.linkedcssresources)) {
      for (i = 0, l = this.linkedcssresources.length; i < l; i++) {
        if (!util.isInstanceOf(this.linkedcssresources[i], CSSResource) && util.isObject(data['linkedcssresources'][i])) {
          this.linkedcssresources[i] = new CSSResource(this.linkedcssresources[i]);
        } else if (!util.isInstanceOf(this.linkedcssresources[i], CSSResource)) {
          throw new Error(util.format('Expected array of CSSResource or an array of Objects but got %s',
            typeof this.linkedcssresources[i]));
        }
      }
    } else {
      this.linkedcssresources = [];
    }

    if (!util.isUndefined(this.linkedjavascriptresources) && util.isArray(this.linkedjavascriptresources)) {
      for (i = 0, l = this.linkedjavascriptresources.length; i < l; i++) {
        if (!util.isInstanceOf(this.linkedjavascriptresources[i], JavaScriptResource) && util.isObject(data['linkedjavascriptresources'][i])) {
          this.linkedjavascriptresources[i] = new JavaScriptResource(this.linkedjavascriptresources[i]);
        } else if (!util.isInstanceOf(this.linkedjavascriptresources[i], JavaScriptResource)) {
          throw new Error(util.format('Expected array of JavaScriptResource or an array of Objects but got %s',
            typeof this.linkedjavascriptresources[i]));
        }
      }
    } else {
      this.linkedjavascriptresources = [];
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get linkedcssresources.
   * @returns {CSSResource[]}
   */
  getLinkedCSSResources() {
    return this.getField('linkedcssresources', []);
  }
  
  /**
   * Get linkedjavascriptresources.
   * @returns {JavaScriptResource[]}
   */
  getLinkedJavaScriptResources() {
    return this.getField('linkedjavascriptresources', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['linkedcssresources'])) {
      for (i = 0, l = ret['linkedcssresources'].length; i < l; i++) {
        if (util.isInstanceOf(ret['linkedcssresources'][i], CSSResource)) {
          ret['linkedcssresources'][i] = ret['linkedcssresources'][i].toObject();
        }
      }
    }

    if (util.isArray(ret['linkedjavascriptresources'])) {
      for (i = 0, l = ret['linkedjavascriptresources'].length; i < l; i++) {
        if (util.isInstanceOf(ret['linkedjavascriptresources'][i], JavaScriptResource)) {
          ret['linkedjavascriptresources'][i] = ret['linkedjavascriptresources'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** MerchantVersion data model. */
class MerchantVersion extends Model {
  /**
   * MerchantVersion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get version.
   * @returns {string}
   */
  getVersion() {
    return this.getField('version');
  }
  
  /**
   * Get major.
   * @returns {number}
   */
  getMajor() {
    return this.getField('major', 0);
  }
  
  /**
   * Get minor.
   * @returns {number}
   */
  getMinor() {
    return this.getField('minor', 0);
  }
  
  /**
   * Get bugfix.
   * @returns {number}
   */
  getBugfix() {
    return this.getField('bugfix', 0);
  }
}

/** CACHE_TYPE constants. */
/** @ignore */
const CACHE_TYPE_NONE = '';
/** @ignore */
const CACHE_TYPE_REDIS = 'redis';

/** Store data model. */
class Store extends Model {
  /**
   * Store Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Constant CACHE_TYPE_NONE
   * @returns {string}
   * @const
   * @static
   */
  static get CACHE_TYPE_NONE() {
    return CACHE_TYPE_NONE;
  }

  /**
   * Constant CACHE_TYPE_REDIS
   * @returns {string}
   * @const
   * @static
   */
  static get CACHE_TYPE_REDIS() {
    return CACHE_TYPE_REDIS;
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get manager_id.
   * @returns {number}
   */
  getManagerId() {
    return this.getField('manager_id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get license.
   * @returns {string}
   */
  getLicense() {
    return this.getField('license');
  }
  
  /**
   * Get name.
   * @returns {string}
   */
  getName() {
    return this.getField('name');
  }
  
  /**
   * Get owner.
   * @returns {string}
   */
  getOwner() {
    return this.getField('owner');
  }
  
  /**
   * Get email.
   * @returns {string}
   */
  getEmail() {
    return this.getField('email');
  }
  
  /**
   * Get company.
   * @returns {string}
   */
  getCompany() {
    return this.getField('company');
  }
  
  /**
   * Get address.
   * @returns {string}
   */
  getAddress() {
    return this.getField('address');
  }
  
  /**
   * Get city.
   * @returns {string}
   */
  getCity() {
    return this.getField('city');
  }
  
  /**
   * Get state.
   * @returns {string}
   */
  getState() {
    return this.getField('state');
  }
  
  /**
   * Get zip.
   * @returns {string}
   */
  getZip() {
    return this.getField('zip');
  }
  
  /**
   * Get phone.
   * @returns {string}
   */
  getPhone() {
    return this.getField('phone');
  }
  
  /**
   * Get fax.
   * @returns {string}
   */
  getFax() {
    return this.getField('fax');
  }
  
  /**
   * Get country.
   * @returns {string}
   */
  getCountry() {
    return this.getField('country');
  }
  
  /**
   * Get wtunits.
   * @returns {string}
   */
  getWeightUnits() {
    return this.getField('wtunits');
  }
  
  /**
   * Get wtunitcode.
   * @returns {string}
   */
  getWeightUnitCode() {
    return this.getField('wtunitcode');
  }
  
  /**
   * Get dmunitcode.
   * @returns {string}
   */
  getDimensionUnits() {
    return this.getField('dmunitcode');
  }
  
  /**
   * Get baskexp.
   * @returns {number}
   */
  getBasketExpiration() {
    return this.getField('baskexp', 0);
  }
  
  /**
   * Get pgrp_ovlp.
   * @returns {string}
   */
  getPriceGroupOverlapResolution() {
    return this.getField('pgrp_ovlp');
  }
  
  /**
   * Get ui_id.
   * @returns {number}
   */
  getUserInterfaceId() {
    return this.getField('ui_id', 0);
  }
  
  /**
   * Get tax_id.
   * @returns {number}
   */
  getTaxId() {
    return this.getField('tax_id', 0);
  }
  
  /**
   * Get currncy_id.
   * @returns {number}
   */
  getCurrencyId() {
    return this.getField('currncy_id', 0);
  }
  
  /**
   * Get mnt_warn.
   * @returns {string}
   */
  getMaintenanceWarningMessage() {
    return this.getField('mnt_warn');
  }
  
  /**
   * Get mnt_close.
   * @returns {string}
   */
  getMaintenanceClosedMessage() {
    return this.getField('mnt_close');
  }
  
  /**
   * Get mnt_time.
   * @returns {number}
   */
  getMaintenanceTime() {
    return this.getField('mnt_time', 0);
  }
  
  /**
   * Get mnt_no_new.
   * @returns {number}
   */
  getMaintenanceNoNewCustomersBefore() {
    return this.getField('mnt_no_new', 0);
  }
  
  /**
   * Get omin_quant.
   * @returns {number}
   */
  getOrderMinimumQuantity() {
    return this.getField('omin_quant', 0);
  }
  
  /**
   * Get omin_price.
   * @returns {foat}
   */
  getOrderMinimumPrice() {
    // Missing foat [5]
  }
  
  /**
   * Get omin_all.
   * @returns {boolean}
   */
  getOrderMinimumRequiredAll() {
    return this.getField('omin_all', false);
  }
  
  /**
   * Get omin_msg.
   * @returns {string}
   */
  getOrderMinimumMessage() {
    return this.getField('omin_msg');
  }
  
  /**
   * Get crypt_id.
   * @returns {number}
   */
  getCryptId() {
    return this.getField('crypt_id', 0);
  }
  
  /**
   * Get req_ship.
   * @returns {boolean}
   */
  getRequireShipping() {
    return this.getField('req_ship', false);
  }
  
  /**
   * Get req_tax.
   * @returns {boolean}
   */
  getRequireTax() {
    return this.getField('req_tax', false);
  }
  
  /**
   * Get req_frship.
   * @returns {boolean}
   */
  getRequireFreeOrderShipping() {
    return this.getField('req_frship', false);
  }
  
  /**
   * Get item_adel.
   * @returns {boolean}
   */
  getItemModuleUninstallable() {
    return this.getField('item_adel', false);
  }
  
  /**
   * Get cache_type.
   * @returns {string}
   */
  getCacheType() {
    return this.getField('cache_type');
  }
  
  /**
   * Get redishost.
   * @returns {string}
   */
  getRedisHost() {
    return this.getField('redishost');
  }
  
  /**
   * Get redisport.
   * @returns {number}
   */
  getRedisPort() {
    return this.getField('redisport', 0);
  }
  
  /**
   * Get redisto.
   * @returns {number}
   */
  getRedisTimeout() {
    return this.getField('redisto', 0);
  }
  
  /**
   * Get redisex.
   * @returns {number}
   */
  getRedisExpiration() {
    return this.getField('redisex', 0);
  }
}

/** CustomerAddressList data model. */
class CustomerAddressList extends Model {
  /**
   * CustomerAddressList Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.addresses) && util.isArray(this.addresses)) {
      for (i = 0, l = this.addresses.length; i < l; i++) {
        if (!util.isInstanceOf(this.addresses[i], CustomerAddress) && util.isObject(data['addresses'][i])) {
          this.addresses[i] = new CustomerAddress(this.addresses[i]);
        } else if (!util.isInstanceOf(this.addresses[i], CustomerAddress)) {
          throw new Error(util.format('Expected array of CustomerAddress or an array of Objects but got %s',
            typeof this.addresses[i]));
        }
      }
    } else {
      this.addresses = [];
    }
  }

  /**
   * Get ship_id.
   * @returns {number}
   */
  getShipId() {
    return this.getField('ship_id', 0);
  }
  
  /**
   * Get bill_id.
   * @returns {number}
   */
  getBillId() {
    return this.getField('bill_id', 0);
  }
  
  /**
   * Get addresses.
   * @returns {CustomerAddress[]}
   */
  getAddresses() {
    return this.getField('addresses', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['addresses'])) {
      for (i = 0, l = ret['addresses'].length; i < l; i++) {
        if (util.isInstanceOf(ret['addresses'][i], CustomerAddress)) {
          ret['addresses'][i] = ret['addresses'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** VariantAttribute data model. */
class VariantAttribute extends Model {
  /**
   * VariantAttribute Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get attr_id.
   * @returns {number}
   */
  getAttributeId() {
    return this.getField('attr_id', 0);
  }
  
  /**
   * Get attmpat_id.
   * @returns {number}
   */
  getAttributeTemplateAttributeId() {
    return this.getField('attmpat_id', 0);
  }
  
  /**
   * Get option_id.
   * @returns {number}
   */
  getOptionId() {
    return this.getField('option_id', 0);
  }
  
  /**
   * Set attr_id.
   * @param {number} attributeId
   * @returns {VariantAttribute}
   */
  setAttributeId(attributeId) {
    return this.setField('attr_id', attributeId);
  }

  /**
   * Set attmpat_id.
   * @param {number} attributeTemplateAttributeId
   * @returns {VariantAttribute}
   */
  setAttributeTemplateAttributeId(attributeTemplateAttributeId) {
    return this.setField('attmpat_id', attributeTemplateAttributeId);
  }

  /**
   * Set option_id.
   * @param {number} optionId
   * @returns {VariantAttribute}
   */
  setOptionId(optionId) {
    return this.setField('option_id', optionId);
  }
}

/** VariantPart data model. */
class VariantPart extends Model {
  /**
   * VariantPart Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get part_id.
   * @returns {number}
   */
  getPartId() {
    return this.getField('part_id', 0);
  }
  
  /**
   * Get quantity.
   * @returns {number}
   */
  getQuantity() {
    return this.getField('quantity', 0);
  }
  
  /**
   * Set part_id.
   * @param {number} partId
   * @returns {VariantPart}
   */
  setPartId(partId) {
    return this.setField('part_id', partId);
  }

  /**
   * Set quantity.
   * @param {number} quantity
   * @returns {VariantPart}
   */
  setQuantity(quantity) {
    return this.setField('quantity', quantity);
  }
}

/** ImageType data model. */
class ImageType extends Model {
  /**
   * ImageType Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get descrip.
   * @returns {string}
   */
  getDescription() {
    return this.getField('descrip');
  }
}

/** EXCLUSION_SCOPE constants. */
/** @ignore */
const EXCLUSION_SCOPE_BASKET = 'basket';
/** @ignore */
const EXCLUSION_SCOPE_GROUP = 'group';
/** @ignore */
const EXCLUSION_SCOPE_ITEM = 'item';

/** PriceGroupExclusion data model. */
class PriceGroupExclusion extends Model {
  /**
   * PriceGroupExclusion Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Constant EXCLUSION_SCOPE_BASKET
   * @returns {string}
   * @const
   * @static
   */
  static get EXCLUSION_SCOPE_BASKET() {
    return EXCLUSION_SCOPE_BASKET;
  }

  /**
   * Constant EXCLUSION_SCOPE_GROUP
   * @returns {string}
   * @const
   * @static
   */
  static get EXCLUSION_SCOPE_GROUP() {
    return EXCLUSION_SCOPE_GROUP;
  }

  /**
   * Constant EXCLUSION_SCOPE_ITEM
   * @returns {string}
   * @const
   * @static
   */
  static get EXCLUSION_SCOPE_ITEM() {
    return EXCLUSION_SCOPE_ITEM;
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get scope.
   * @returns {string}
   */
  getScope() {
    return this.getField('scope');
  }
  
  /**
   * Set id.
   * @param {number} id
   * @returns {PriceGroupExclusion}
   */
  setId(id) {
    return this.setField('id', id);
  }

  /**
   * Set scope.
   * @param {string} scope
   * @returns {PriceGroupExclusion}
   */
  setScope(scope) {
    return this.setField('scope', scope);
  }
}

/** AttributeTemplate data model. */
class AttributeTemplate extends Model {
  /**
   * AttributeTemplate Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get prompt.
   * @returns {string}
   */
  getPrompt() {
    return this.getField('prompt');
  }
  
  /**
   * Get refcount.
   * @returns {number}
   */
  getRefcount() {
    return this.getField('refcount', 0);
  }
}

/** TEMPLATE_ATTRIBUTE_TYPE constants. */
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_CHECKBOX = 'checkbox';
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_RADIO = 'radio';
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_TEXT = 'text';
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_SELECT = 'select';
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_MEMO = 'memo';
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_TEMPLATE = 'template';
/** @ignore */
const TEMPLATE_ATTRIBUTE_TYPE_SWATCH_SELECT = 'swatch-select';

/** AttributeTemplateAttribute data model. */
class AttributeTemplateAttribute extends Model {
  /**
   * AttributeTemplateAttribute Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.options) && util.isArray(this.options)) {
      for (i = 0, l = this.options.length; i < l; i++) {
        if (!util.isInstanceOf(this.options[i], AttributeTemplateOption) && util.isObject(data['options'][i])) {
          this.options[i] = new AttributeTemplateOption(this.options[i]);
        } else if (!util.isInstanceOf(this.options[i], AttributeTemplateOption)) {
          throw new Error(util.format('Expected array of AttributeTemplateOption or an array of Objects but got %s',
            typeof this.options[i]));
        }
      }
    } else {
      this.options = [];
    }
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_CHECKBOX
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_CHECKBOX() {
    return TEMPLATE_ATTRIBUTE_TYPE_CHECKBOX;
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_RADIO
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_RADIO() {
    return TEMPLATE_ATTRIBUTE_TYPE_RADIO;
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_TEXT
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_TEXT() {
    return TEMPLATE_ATTRIBUTE_TYPE_TEXT;
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_SELECT
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_SELECT() {
    return TEMPLATE_ATTRIBUTE_TYPE_SELECT;
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_MEMO
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_MEMO() {
    return TEMPLATE_ATTRIBUTE_TYPE_MEMO;
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_TEMPLATE
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_TEMPLATE() {
    return TEMPLATE_ATTRIBUTE_TYPE_TEMPLATE;
  }

  /**
   * Constant TEMPLATE_ATTRIBUTE_TYPE_SWATCH_SELECT
   * @returns {string}
   * @const
   * @static
   */
  static get TEMPLATE_ATTRIBUTE_TYPE_SWATCH_SELECT() {
    return TEMPLATE_ATTRIBUTE_TYPE_SWATCH_SELECT;
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get attemp_id.
   * @returns {number}
   */
  getAttributeTemplateId() {
    return this.getField('attemp_id', 0);
  }
  
  /**
   * Get default_id.
   * @returns {number}
   */
  getDefaultId() {
    return this.getField('default_id', 0);
  }
  
  /**
   * Get disp_order.
   * @returns {number}
   */
  getDisplayOrder() {
    if (this.hasField('disp_order')) {
      return this.getField('disp_order', 0);
    } else if (this.hasField('disporder')) {
      return this.getField('disporder', 0);
    }
    return 0;
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get prompt.
   * @returns {string}
   */
  getPrompt() {
    return this.getField('prompt');
  }
  
  /**
   * Get price.
   * @returns {number}
   */
  getPrice() {
    return this.getField('price', 0.00);
  }
  
  /**
   * Get cost.
   * @returns {number}
   */
  getCost() {
    return this.getField('cost', 0.00);
  }
  
  /**
   * Get weight.
   * @returns {number}
   */
  getWeight() {
    return this.getField('weight', 0.00);
  }
  
  /**
   * Get required.
   * @returns {boolean}
   */
  getRequired() {
    return this.getField('required', false);
  }
  
  /**
   * Get inventory.
   * @returns {boolean}
   */
  getInventory() {
    return this.getField('inventory', false);
  }
  
  /**
   * Get image.
   * @returns {string}
   */
  getImage() {
    return this.getField('image');
  }
  
  /**
   * Get options.
   * @returns {AttributeTemplateOption[]}
   */
  getOptions() {
    return this.getField('options', []);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['options'])) {
      for (i = 0, l = ret['options'].length; i < l; i++) {
        if (util.isInstanceOf(ret['options'][i], AttributeTemplateOption)) {
          ret['options'][i] = ret['options'][i].toObject();
        }
      }
    }

    return ret;
  }
}

/** AttributeTemplateOption data model. */
class AttributeTemplateOption extends Model {
  /**
   * AttributeTemplateOption Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get attemp_id.
   * @returns {}
   */
  getAttributeTemplateId() {
    // Missing  [5]
  }
  
  /**
   * Get attmpat_id.
   * @returns {number}
   */
  getAttributeTemplateAttributeId() {
    return this.getField('attmpat_id', 0);
  }
  
  /**
   * Get disporder.
   * @returns {number}
   */
  getDisplayOrder() {
    if (this.hasField('disporder')) {
      return this.getField('disporder', 0);
    } else if (this.hasField('disp_order')) {
      return this.getField('disp_order', 0);
    }
    return 0;
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get prompt.
   * @returns {string}
   */
  getPrompt() {
    return this.getField('prompt');
  }
  
  /**
   * Get price.
   * @returns {number}
   */
  getPrice() {
    return this.getField('price', 0.00);
  }
  
  /**
   * Get cost.
   * @returns {number}
   */
  getCost() {
    return this.getField('cost', 0.00);
  }
  
  /**
   * Get weight.
   * @returns {number}
   */
  getWeight() {
    return this.getField('weight', 0.00);
  }
  
  /**
   * Get image.
   * @returns {string}
   */
  getImage() {
    return this.getField('image');
  }
  
  /**
   * Get formatted_price.
   * @returns {string}
   */
  getFormattedPrice() {
    return this.getField('formatted_price');
  }
  
  /**
   * Get formatted_cost.
   * @returns {string}
   */
  getFormattedCost() {
    return this.getField('formatted_cost');
  }
  
  /**
   * Get default_opt.
   * @returns {boolean}
   */
  getDefaultOpt() {
    return this.getField('default_opt', false);
  }
}

/** OrderPart data model. */
class OrderPart extends Model {
  /**
   * OrderPart Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get sku.
   * @returns {string}
   */
  getSku() {
    return this.getField('sku');
  }
  
  /**
   * Get name.
   * @returns {string}
   */
  getName() {
    return this.getField('name');
  }
  
  /**
   * Get quantity.
   * @returns {number}
   */
  getQuantity() {
    return this.getField('quantity', 0);
  }
  
  /**
   * Get total_quantity.
   * @returns {number}
   */
  getTotalQuantity() {
    return this.getField('total_quantity', 0);
  }
  
  /**
   * Get price.
   * @returns {number}
   */
  getPrice() {
    return this.getField('price', 0.00);
  }
}

/** ProductAttributeListAttribute data model. */
class ProductAttributeListAttribute extends Model {
  /**
   * ProductAttributeListAttribute Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    var i;
    var l;

    super(data);

    if (!util.isUndefined(this.attributes) && util.isArray(this.attributes)) {
      for (i = 0, l = this.attributes.length; i < l; i++) {
        if (!util.isInstanceOf(this.attributes[i], ProductAttributeListAttribute) && util.isObject(data['attributes'][i])) {
          this.attributes[i] = new ProductAttributeListAttribute(this.attributes[i]);
        } else if (!util.isInstanceOf(this.attributes[i], ProductAttributeListAttribute)) {
          throw new Error(util.format('Expected array of ProductAttributeListAttribute or an array of Objects but got %s',
            typeof this.attributes[i]));
        }
      }
    } else {
      this.attributes = [];
    }

    if (!util.isUndefined(this.options) && util.isArray(this.options)) {
      for (i = 0, l = this.options.length; i < l; i++) {
        if (!util.isInstanceOf(this.options[i], ProductOption) && util.isObject(data['options'][i])) {
          this.options[i] = new ProductOption(this.options[i]);
        } else if (!util.isInstanceOf(this.options[i], ProductOption)) {
          throw new Error(util.format('Expected array of ProductOption or an array of Objects but got %s',
            typeof this.options[i]));
        }
      }
    } else {
      this.options = [];
    }

    if (!util.isUndefined(this.template)) {
      if (!util.isInstanceOf(this.template, ProductAttributeListTemplate) && util.isObject(this.template)) {
        this.template = new ProductAttributeListTemplate(this.template);
      } else if (!util.isInstanceOf(this.template, ProductAttributeListTemplate)) {
        throw new Error(util.format('Expected ProductAttributeListTemplate or an Object but got %s',
          typeof this.template));
      }
    } else {
      this.template = {};
    }
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get default_id.
   * @returns {number}
   */
  getDefaultId() {
    return this.getField('default_id', 0);
  }
  
  /**
   * Get disp_order.
   * @returns {number}
   */
  getDisplayOrder() {
    if (this.hasField('disp_order')) {
      return this.getField('disp_order', 0);
    } else if (this.hasField('disporder')) {
      return this.getField('disporder', 0);
    }
    return 0;
  }
  
  /**
   * Get attemp_id.
   * @returns {number}
   */
  getAttributeTemplateId() {
    return this.getField('attemp_id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get type.
   * @returns {string}
   */
  getType() {
    return this.getField('type');
  }
  
  /**
   * Get prompt.
   * @returns {string}
   */
  getPrompt() {
    return this.getField('prompt');
  }
  
  /**
   * Get price.
   * @returns {number}
   */
  getPrice() {
    return this.getField('price', 0.00);
  }
  
  /**
   * Get cost.
   * @returns {number}
   */
  getCost() {
    return this.getField('cost', 0.00);
  }
  
  /**
   * Get weight.
   * @returns {number}
   */
  getWeight() {
    return this.getField('weight', 0.00);
  }
  
  /**
   * Get required.
   * @returns {boolean}
   */
  getRequired() {
    return this.getField('required', false);
  }
  
  /**
   * Get inventory.
   * @returns {boolean}
   */
  getInventory() {
    return this.getField('inventory', false);
  }
  
  /**
   * Get image.
   * @returns {string}
   */
  getImage() {
    return this.getField('image');
  }
  
  /**
   * Get attributes.
   * @returns {ProductAttributeListAttribute[]}
   */
  getTemplateAttributes() {
    return this.getField('attributes', []);
  }
  
  /**
   * Get options.
   * @returns {ProductOption[]}
   */
  getOptions() {
    return this.getField('options', []);
  }
  
  /**
   * Get has_variant_parts.
   * @returns {boolean}
   */
  getHasVariantParts() {
    return this.getField('has_variant_parts', false);
  }
  
  /**
   * Get template.
   * @returns {ProductAttributeListTemplate|*}
   */
  getTemplate() {
    return this.getField('template', null);
  }
  
  /**
   * @override
   */
  toObject() {
    var i;
    var l;
    var ret = Object.assign(this);

    if (util.isArray(ret['attributes'])) {
      for (i = 0, l = ret['attributes'].length; i < l; i++) {
        if (util.isInstanceOf(ret['attributes'][i], ProductAttributeListAttribute)) {
          ret['attributes'][i] = ret['attributes'][i].toObject();
        }
      }
    }

    if (util.isArray(ret['options'])) {
      for (i = 0, l = ret['options'].length; i < l; i++) {
        if (util.isInstanceOf(ret['options'][i], ProductOption)) {
          ret['options'][i] = ret['options'][i].toObject();
        }
      }
    }

    if (util.isInstanceOf(ret['template'], ProductAttributeListTemplate)) {
      ret['template'] = ret['template'].toObject();
    }

    return ret;
  }
}

/** ProductAttributeListOption data model. */
class ProductAttributeListOption extends Model {
  /**
   * ProductAttributeListOption Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get product_id.
   * @returns {number}
   */
  getProductId() {
    return this.getField('product_id', 0);
  }
  
  /**
   * Get attr_id.
   * @returns {number}
   */
  getAttributeId() {
    return this.getField('attr_id', 0);
  }
  
  /**
   * Get attemp_id.
   * @returns {number}
   */
  getAttributeTemplateId() {
    return this.getField('attemp_id', 0);
  }
  
  /**
   * Get attmpat_id.
   * @returns {number}
   */
  getAttributeTemplateAttributeId() {
    return this.getField('attmpat_id', 0);
  }
  
  /**
   * Get disp_order.
   * @returns {number}
   */
  getDisplayOrder() {
    if (this.hasField('disp_order')) {
      return this.getField('disp_order', 0);
    } else if (this.hasField('disporder')) {
      return this.getField('disporder', 0);
    }
    return 0;
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get prompt.
   * @returns {string}
   */
  getPrompt() {
    return this.getField('prompt');
  }
  
  /**
   * Get price.
   * @returns {number}
   */
  getPrice() {
    return this.getField('price', 0.00);
  }
  
  /**
   * Get cost.
   * @returns {number}
   */
  getCost() {
    return this.getField('cost', 0.00);
  }
  
  /**
   * Get weight.
   * @returns {number}
   */
  getWeight() {
    return this.getField('weight', 0.00);
  }
  
  /**
   * Get image.
   * @returns {string}
   */
  getImage() {
    return this.getField('image');
  }
  
  /**
   * Get default_opt.
   * @returns {boolean}
   */
  getDefaultOption() {
    return this.getField('default_opt', false);
  }
}

/** ProductAttributeListTemplate data model. */
class ProductAttributeListTemplate extends Model {
  /**
   * ProductAttributeListTemplate Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get id.
   * @returns {number}
   */
  getId() {
    return this.getField('id', 0);
  }
  
  /**
   * Get code.
   * @returns {string}
   */
  getCode() {
    return this.getField('code');
  }
  
  /**
   * Get prompt.
   * @returns {string}
   */
  getPrompt() {
    return this.getField('prompt');
  }
  
  /**
   * Get refcount.
   * @returns {number}
   */
  getReferenceCount() {
    return this.getField('refcount', 0);
  }
}

/** AvailabilityGroupCustomer data model. */
class AvailabilityGroupCustomer extends Customer {
  /**
   * AvailabilityGroupCustomer Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get assigned.
   * @returns {boolean}
   */
  getAssigned() {
    return this.getField('assigned', false);
  }
}

/** AvailabilityGroupCategory data model. */
class AvailabilityGroupCategory extends Category {
  /**
   * AvailabilityGroupCategory Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get assigned.
   * @returns {boolean}
   */
  getAssigned() {
    return this.getField('assigned', false);
  }
}

/** AvailabilityGroupProduct data model. */
class AvailabilityGroupProduct extends Product {
  /**
   * AvailabilityGroupProduct Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get assigned.
   * @returns {boolean}
   */
  getAssigned() {
    return this.getField('assigned', false);
  }
}

/** AvailabilityGroupBusinessAccount data model. */
class AvailabilityGroupBusinessAccount extends BusinessAccount {
  /**
   * AvailabilityGroupBusinessAccount Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get assigned.
   * @returns {boolean}
   */
  getAssigned() {
    return this.getField('assigned', false);
  }
}

/** BusinessAccountCustomer data model. */
class BusinessAccountCustomer extends Customer {
  /**
   * BusinessAccountCustomer Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }

  /**
   * Get assigned.
   * @returns {boolean}
   */
  getAssigned() {
    return this.getField('assigned', false);
  }
}

/** OrderNote data model. */
class OrderNote extends Note {
  /**
   * OrderNote Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }
}

/** CategoryProduct data model. */
class CategoryProduct extends Product {
  /**
   * CategoryProduct Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }
}

/** AttributeTemplateProduct data model. */
class AttributeTemplateProduct extends Product {
  /**
   * AttributeTemplateProduct Constructor.
   * @param {Object} data
   * @returns {void}
   */
  constructor(data = {}) {
    super(data);
  }
}





