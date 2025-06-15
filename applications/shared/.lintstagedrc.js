module.exports = {
  // TypeScript and JavaScript files
  '*.{ts,tsx,js,jsx}': [
    // Run ESLint with auto-fix
    'eslint --fix',
    // Format with Prettier
    'prettier --write',
    // Add back to git staging
    'git add'
  ],
  
  // JSON files
  '*.json': [
    'prettier --write',
    'git add'
  ],
  
  // Markdown files
  '*.md': [
    'prettier --write',
    'git add'
  ],
  
  // YAML files
  '*.{yml,yaml}': [
    'prettier --write',
    'git add'
  ],
  
  // CSS and SCSS files
  '*.{css,scss,sass}': [
    'prettier --write',
    'git add'
  ],
  
  // ACGS-specific file patterns
  
  // Service configuration files - validate JSON structure
  '**/services/**/*.json': [
    'node -e "JSON.parse(require(\'fs\').readFileSync(process.argv[1], \'utf8\'))"',
    'prettier --write',
    'git add'
  ],
  
  // Component files - ensure proper exports and imports
  '**/components/**/*.{ts,tsx}': [
    'eslint --fix',
    'prettier --write',
    // Custom validation for ACGS component patterns
    'node -e "const content = require(\'fs\').readFileSync(process.argv[1], \'utf8\'); if (content.includes(\'export default\') && !content.includes(\'export {\')) { console.log(\'✅ Component export pattern valid\'); } else if (!content.includes(\'export\')) { console.error(\'❌ Component must have exports\'); process.exit(1); }"',
    'git add'
  ],
  
  // Hook files - validate hook naming convention
  '**/hooks/**/*.{ts,tsx}': [
    'eslint --fix',
    'prettier --write',
    // Validate hook naming (must start with 'use')
    'node -e "const path = require(\'path\'); const filename = path.basename(process.argv[1], path.extname(process.argv[1])); if (!filename.startsWith(\'use\')) { console.error(\'❌ Hook files must start with \\\'use\\\'\'); process.exit(1); } console.log(\'✅ Hook naming convention valid\');"',
    'git add'
  ],
  
  // Service files - validate service integration patterns
  '**/services/**/*.{ts,js}': [
    'eslint --fix',
    'prettier --write',
    // Check for proper error handling in service files
    'node -e "const content = require(\'fs\').readFileSync(process.argv[1], \'utf8\'); if (content.includes(\'try\') && content.includes(\'catch\')) { console.log(\'✅ Service error handling present\'); } else { console.warn(\'⚠️  Consider adding error handling to service file\'); }"',
    'git add'
  ],
  
  // Type definition files - validate TypeScript interfaces
  '**/types/**/*.ts': [
    'eslint --fix',
    'prettier --write',
    // Validate that type files export interfaces or types
    'node -e "const content = require(\'fs\').readFileSync(process.argv[1], \'utf8\'); if (content.includes(\'export interface\') || content.includes(\'export type\') || content.includes(\'export {\')) { console.log(\'✅ Type definitions valid\'); } else { console.error(\'❌ Type files must export interfaces or types\'); process.exit(1); }"',
    'git add'
  ],
  
  // Story files - validate Storybook story structure
  '*.stories.{ts,tsx,js,jsx}': [
    'eslint --fix',
    'prettier --write',
    // Validate story structure
    'node -e "const content = require(\'fs\').readFileSync(process.argv[1], \'utf8\'); if (content.includes(\'export default\') && content.includes(\'Meta\')) { console.log(\'✅ Storybook story structure valid\'); } else { console.warn(\'⚠️  Story file may be missing proper Meta export\'); }"',
    'git add'
  ],
  
  // Test files - validate test structure
  '*.{test,spec}.{ts,tsx,js,jsx}': [
    'eslint --fix',
    'prettier --write',
    // Validate test structure
    'node -e "const content = require(\'fs\').readFileSync(process.argv[1], \'utf8\'); if (content.includes(\'describe\') || content.includes(\'test\') || content.includes(\'it\')) { console.log(\'✅ Test structure valid\'); } else { console.warn(\'⚠️  Test file may be missing test cases\'); }"',
    'git add'
  ]
};
