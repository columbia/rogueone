// This function is copied from eslint_scope 4.0.0 to debug an infinite loop
function updateDeeply(target, override) {

    /**
     * Is hash object
     * @param {Object} value - Test value
     * @returns {boolean} Result
     */
    function isHashObject(value) {
        return typeof value === "object" && value instanceof Object && !(value instanceof Array) && !(value instanceof RegExp);
    }

    for (const key in override) {
        if (override.hasOwnProperty(key)) {
            const val = override[key];

            if (isHashObject(val)) {
                if (isHashObject(target[key])) {
                    updateDeeply(target[key], val);
                } else {
                    target[key] = updateDeeply({}, val);
                }
            } else {
                target[key] = val;
            }
        }
    }
    return target;
}
function analyze(tree, providedOptions) {
    const options = updateDeeply(defaultOptions(), providedOptions);
    const scopeManager = new ScopeManager(options);
    const referencer = new Referencer(options, scopeManager);

    referencer.visit(tree);

    assert(scopeManager.__currentScope === null, "currentScope should be null.");

    return scopeManager;
}
function defaultOptions() {
    return {
        optimistic: false,
        directive: false,
        nodejsScope: false,
        impliedStrict: false,
        sourceType: "script",  // one of ['script', 'module']
        ecmaVersion: 5,
        childVisitorKeys: null,
        fallback: "iteration"
    };
}
module.exports = {

    /** @name module:escope.version */
    version,

    /** @name module:escope.Reference */
    Reference,

    /** @name module:escope.Variable */
    Variable,

    /** @name module:escope.Scope */
    Scope,

    /** @name module:escope.ScopeManager */
    ScopeManager,
    analyze
};
updateDeeply(defaultOptions(), {'hey': 'what', 'blah':{'level2': 4})
