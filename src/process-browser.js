// Custom process polyfill for browser environments
const processObject = {
  browser: true,
  env: {
    NODE_ENV: typeof process !== 'undefined' && process.env ? process.env.NODE_ENV : 'development'
  },
  version: '',
  versions: {},
  nextTick: function(cb) {
    setTimeout(cb, 0);
  }
};

// Make it available globally
if (typeof window !== 'undefined') {
  window.process = window.process || processObject;
}

export default processObject; 