const util = require('node:util');
if (typeof util.styleText === 'function') {
  const orig = util.styleText;
  util.styleText = (format, text) => {
    if (Array.isArray(format)) {
      return format.reduce((acc, f) => orig(f, acc), text);
    }
    return orig(format, text);
  };
}
