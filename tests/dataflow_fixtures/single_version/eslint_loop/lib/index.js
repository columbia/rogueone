function updateDeeply(target, override) {
    for (const key in override) {
        if (override.blah(key)) {
            updateDeeply(target[key], override[key]);
        }
    }
    return target;
}
 
function analyze(providedOptions) {
    updateDeeply({}, providedOptions);
}

module.exports = {
    analyze
};


/* vim: set sw=4 ts=4 et tw=80 : */
