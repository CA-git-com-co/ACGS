import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for ACGS-PGP Framework E2E tests
 * 
 * Prepares the test environment, including mock service setup
 * and authentication state for governance workflow testing.
 */
async function globalSetup(config: FullConfig) {
  console.log('🏛️ Setting up ACGS-PGP Framework E2E test environment...');

  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Wait for Storybook to be ready
    const baseURL = config.projects[0].use.baseURL || 'http://localhost:6006';
    console.log(`📚 Waiting for Storybook at ${baseURL}...`);
    
    await page.goto(baseURL, { waitUntil: 'networkidle' });
    
    // Verify Storybook is loaded
    await page.waitForSelector('[data-testid="storybook-explorer-tree"]', { timeout: 30000 });
    console.log('✅ Storybook is ready');

    // Setup mock ACGS service responses
    await page.route('**/api/v1/principles**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          principles: [
            {
              id: 'PRIN-001',
              title: 'Democratic Governance',
              content: 'All policy changes must be approved through democratic voting',
              category: 'governance',
              priority: 9,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              author: 'system'
            }
          ]
        })
      });
    });

    await page.route('**/api/v1/synthesize**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          policies: [
            {
              id: 'POL-001',
              name: 'Synthesized Governance Policy',
              description: 'Policy synthesized from constitutional principles',
              rules: [
                {
                  id: 'R1',
                  condition: 'action.requiresGovernance === true',
                  action: 'REQUIRE_APPROVAL'
                }
              ],
              validationScore: 95,
              complianceComplexity: 25,
              status: 'active',
              category: 'governance',
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              author: 'gs-engine'
            }
          ],
          validationScore: 95,
          complianceComplexity: 25
        })
      });
    });

    await page.route('**/api/v1/compliance**', async route => {
      const request = route.request();
      const postData = request.postData();
      
      // Mock compliance check based on request
      let compliant = true;
      let confidenceScore = 95;
      let violationReasons: string[] | undefined;

      if (postData?.includes('unauthorized') || postData?.includes('violation')) {
        compliant = false;
        confidenceScore = 85;
        violationReasons = ['Action violates governance policy'];
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          compliant,
          confidenceScore,
          violationReasons
        })
      });
    });

    // Setup authentication mock
    await page.route('**/auth/login**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: {
            id: 'user-123',
            username: 'testuser',
            email: 'test@acgs.dev',
            role: 'admin'
          },
          token: 'mock-jwt-token'
        })
      });
    });

    console.log('🔧 Mock services configured');

    // Store authentication state for tests
    await page.evaluate(() => {
      localStorage.setItem('acgs-auth-token', 'mock-jwt-token');
      localStorage.setItem('acgs-user', JSON.stringify({
        id: 'user-123',
        username: 'testuser',
        email: 'test@acgs.dev',
        role: 'admin'
      }));
    });

    console.log('🔐 Authentication state prepared');

  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }

  console.log('✅ ACGS-PGP Framework E2E setup completed');
}

export default globalSetup;
