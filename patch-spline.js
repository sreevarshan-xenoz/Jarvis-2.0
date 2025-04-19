const fs = require('fs');
const path = require('path');

// Path to Spline runtime file
const splineRuntimePath = path.resolve(__dirname, 'node_modules/@splinetool/runtime/build/runtime.js');

// Check if file exists
if (fs.existsSync(splineRuntimePath)) {
  console.log('Patching Spline runtime file...');
  
  // Read the file
  let content = fs.readFileSync(splineRuntimePath, 'utf8');
  
  // Replace problematic imports
  content = content.replace(/require\(['"]process\/browser['"]\)/g, '{ browser: true }');
  
  // Write back the patched file
  fs.writeFileSync(splineRuntimePath, content);
  
  console.log('Spline runtime patched successfully!');
} else {
  console.error('Spline runtime file not found!');
} 