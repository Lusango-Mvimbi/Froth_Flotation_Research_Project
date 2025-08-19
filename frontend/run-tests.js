/**
 * Frontend Test Runner
 * ===================
 * 
 * Script to run all frontend tests and generate reports.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Running Frontend Tests...\n');

try {
  // Run Jest tests with coverage
  console.log('📊 Running unit tests with coverage...');
  execSync('npm run test:coverage', { 
    stdio: 'inherit',
    cwd: __dirname 
  });

  // Check if coverage report exists
  const coveragePath = path.join(__dirname, 'coverage', 'lcov-report', 'index.html');
  if (fs.existsSync(coveragePath)) {
    console.log('\n✅ Coverage report generated successfully!');
    console.log(`📁 Coverage report: ${coveragePath}`);
  }

  console.log('\n🎉 All frontend tests completed successfully!');

} catch (error) {
  console.error('\n❌ Test execution failed:', error.message);
  process.exit(1);
}
