// Patch for Spline runtime process issues
import './process-browser.js';

// Patch the global environment to ensure process is available
if (typeof window !== 'undefined' && !window.process) {
  window.process = {
    browser: true,
    env: {
      NODE_ENV: process.env.NODE_ENV || 'development'
    },
    version: '',
    versions: {},
    nextTick: function(cb) {
      setTimeout(cb, 0);
    }
  };
}

export default {}; 