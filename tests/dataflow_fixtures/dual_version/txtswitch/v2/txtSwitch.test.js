const txtSwitch = require('./index.js');

test('txtSwitch', () => {
    expect(txtSwitch('abc')).not.toBeUndefined();
})