#!/usr/bin/env node
/**
 * Pretty test for Header navigation categories
 * Verifies all 5 categories are properly configured
 */

const fs = require('fs');
const path = require('path');

console.log('\n' + '🧪'.repeat(40));
console.log('HEADER NAVIGATION TEST');
console.log('🧪'.repeat(40));

// Read Header.tsx
const headerPath = path.join(__dirname, 'components', 'Header.tsx');
const headerContent = fs.readFileSync(headerPath, 'utf8');

// Extract dropdownCategories array
const categoriesMatch = headerContent.match(/const dropdownCategories = \[([\s\S]*?)\] as const/);

if (!categoriesMatch) {
  console.log('\n❌ Could not find dropdownCategories in Header.tsx');
  process.exit(1);
}

// Parse categories
const categoriesText = categoriesMatch[1];
const categoryRegex = /\{ id: '([^']+)', label: '([^']+)' \}/g;
const categories = [];
let match;

while ((match = categoryRegex.exec(categoriesText)) !== null) {
  categories.push({
    id: match[1],
    label: match[2]
  });
}

// Display results
console.log('\n' + '='.repeat(80));
console.log('NAVIGATION CATEGORIES FOUND');
console.log('='.repeat(80));

console.log(`\n✓ Total categories: ${categories.length}`);
console.log('\nCategories configured:\n');

categories.forEach((cat, index) => {
  const icon = index < 3 ? '📦' : '✨'; // Different icon for new categories
  const badge = index >= 3 ? ' [NEW]' : '';
  console.log(`  ${icon} ${index + 1}. ${cat.label}${badge}`);
  console.log(`     ID: ${cat.id}`);
  console.log('');
});

// Verify expected categories
console.log('='.repeat(80));
console.log('VERIFICATION CHECKS');
console.log('='.repeat(80));

const expectedCategories = [
  { id: 'cookware', label: 'COOKWARE' },
  { id: 'knives', label: 'KNIVES' },
  { id: 'bakeware', label: 'BAKEWARE' },
  { id: 'small_appliances', label: 'SMALL APPLIANCES' },
  { id: 'kitchen_tools', label: 'KITCHEN TOOLS' }
];

let allPassed = true;

expectedCategories.forEach((expected, index) => {
  const actual = categories[index];
  const matches = actual && actual.id === expected.id && actual.label === expected.label;

  if (matches) {
    console.log(`\n✓ ${expected.label}`);
    console.log(`  ID matches: ${expected.id}`);
  } else {
    console.log(`\n❌ ${expected.label}`);
    console.log(`  Expected ID: ${expected.id}`);
    console.log(`  Actual: ${actual ? actual.id : 'NOT FOUND'}`);
    allPassed = false;
  }
});

console.log('\n' + '='.repeat(80));

if (allPassed && categories.length === 5) {
  console.log('✅ ALL CHECKS PASSED');
  console.log('='.repeat(80));
  console.log('\nSummary:');
  console.log('  ✓ 5 navigation categories configured');
  console.log('  ✓ Original categories: COOKWARE, KNIVES, BAKEWARE');
  console.log('  ✓ New categories: SMALL APPLIANCES, KITCHEN TOOLS');
  console.log('  ✓ All IDs and labels match expected values');
  console.log('\n🎉 Header navigation is properly configured!');
  console.log('\nNext steps:');
  console.log('  1. Visit http://localhost:3000');
  console.log('  2. Check desktop header for all 5 categories');
  console.log('  3. Check mobile menu (☰) for all 5 categories');
  console.log('  4. Click each category to see dropdown functionality');
  console.log('');
  process.exit(0);
} else {
  console.log('❌ SOME CHECKS FAILED');
  console.log('='.repeat(80));
  console.log(`\nExpected 5 categories, found ${categories.length}`);
  console.log('');
  process.exit(1);
}
