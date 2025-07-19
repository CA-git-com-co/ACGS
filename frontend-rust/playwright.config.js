// ACGS-2 Playwright E2E Testing Configuration
// Constitutional Hash: cdd01ef066bc6cf2
// 
// Comprehensive E2E testing with cross-browser support and visual regression
// Target: >80% critical path coverage with constitutional compliance

const { defineConfig, devices } = require('@playwright/test');

/**
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './tests/e2e',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['line']
  ],
  
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:8080',
    
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
    
    /* Constitutional compliance metadata */
    extraHTTPHeaders: {
      'X-Constitutional-Hash': 'cdd01ef066bc6cf2',
      'X-Test-Framework': 'Playwright',
      'X-Test-Type': 'E2E'
    }
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Enable additional Chrome features for testing
        launchOptions: {
          args: ['--enable-experimental-web-platform-features']
        }
      },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* Test against branded browsers. */
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'trunk serve --port 8080 --address 0.0.0.0',
    url: 'http://localhost:8080',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes
  },
  
  /* Global setup and teardown */
  globalSetup: require.resolve('./tests/e2e/global-setup.js'),
  globalTeardown: require.resolve('./tests/e2e/global-teardown.js'),
  
  /* Test timeout */
  timeout: 30 * 1000, // 30 seconds
  
  /* Expect timeout */
  expect: {
    timeout: 10 * 1000, // 10 seconds
    
    /* Visual comparison threshold */
    toHaveScreenshot: {
      threshold: 0.2,
      mode: 'strict'
    },
    
    toMatchSnapshot: {
      threshold: 0.2,
      mode: 'strict'
    }
  },
  
  /* Output directories */
  outputDir: 'test-results/artifacts',
  
  /* Test metadata */
  metadata: {
    constitutional_hash: 'cdd01ef066bc6cf2',
    framework: 'Playwright',
    target_coverage: '80%',
    test_types: ['functional', 'visual', 'accessibility', 'performance'],
    browsers: ['chromium', 'firefox', 'webkit', 'mobile'],
    version: '1.0.0'
  }
});
