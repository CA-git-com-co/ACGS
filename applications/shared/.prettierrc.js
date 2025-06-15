module.exports = {
  // Core formatting options matching ACGS codebase style
  semi: true,
  trailingComma: 'none',
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  
  // JSX specific options
  jsxSingleQuote: false,
  jsxBracketSameLine: false,
  
  // Other formatting options
  arrowParens: 'avoid',
  bracketSpacing: true,
  endOfLine: 'lf',
  htmlWhitespaceSensitivity: 'css',
  insertPragma: false,
  proseWrap: 'preserve',
  quoteProps: 'as-needed',
  requirePragma: false,
  
  // File-specific overrides for ACGS patterns
  overrides: [
    {
      files: '*.json',
      options: {
        printWidth: 80,
        tabWidth: 2
      }
    },
    {
      files: '*.md',
      options: {
        printWidth: 80,
        proseWrap: 'always'
      }
    },
    {
      files: '*.yml',
      options: {
        tabWidth: 2,
        singleQuote: false
      }
    },
    {
      files: '*.yaml',
      options: {
        tabWidth: 2,
        singleQuote: false
      }
    },
    {
      // Storybook files may have longer lines for story configurations
      files: '*.stories.@(js|jsx|ts|tsx)',
      options: {
        printWidth: 120
      }
    },
    {
      // Configuration files
      files: ['*.config.@(js|ts)', '.eslintrc.js', '.prettierrc.js'],
      options: {
        printWidth: 120,
        trailingComma: 'none'
      }
    }
  ]
};
