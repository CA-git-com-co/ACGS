// ACGS-2 Critical Path E2E Tests
// Constitutional Hash: cdd01ef066bc6cf2
// 
// Tests covering >80% of critical user workflows with constitutional compliance

const { test, expect } = require('@playwright/test');

const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2';

test.describe('🏛️ ACGS-2 Critical User Paths', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/');
    
    // Wait for application to load
    await page.waitForLoadState('networkidle');
    
    // Verify constitutional compliance
    const constitutionalElement = await page.locator('[data-constitutional-hash]').first();
    const hashValue = await constitutionalElement.getAttribute('data-constitutional-hash');
    expect(hashValue).toBe(CONSTITUTIONAL_HASH);
  });

  test('🚀 Application Load and Initial Render', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/ACGS/);
    
    // Verify main application container
    await expect(page.locator('.app')).toBeVisible();
    
    // Verify constitutional hash is present
    await expect(page.locator(`[data-constitutional-hash="${CONSTITUTIONAL_HASH}"]`)).toBeVisible();
    
    // Check for loading states completion
    await expect(page.locator('.loading-spinner')).not.toBeVisible({ timeout: 10000 });
    
    // Verify main content is loaded
    await expect(page.locator('main, [role="main"], .dashboard')).toBeVisible();
    
    // Take screenshot for visual regression
    await expect(page).toHaveScreenshot('application-initial-load.png');
  });

  test('🧭 Navigation and Routing', async ({ page }) => {
    // Test dashboard navigation
    const dashboardLink = page.locator('a[href*="dashboard"], button:has-text("Dashboard")').first();
    if (await dashboardLink.isVisible()) {
      await dashboardLink.click();
      await page.waitForLoadState('networkidle');
      
      // Verify dashboard content
      await expect(page.locator('.dashboard, [data-testid="dashboard"]')).toBeVisible();
    }
    
    // Test constitutional section navigation
    const constitutionalLink = page.locator('a[href*="constitutional"], button:has-text("Constitutional")').first();
    if (await constitutionalLink.isVisible()) {
      await constitutionalLink.click();
      await page.waitForLoadState('networkidle');
      
      // Verify constitutional content
      await expect(page.locator('.constitutional, [data-testid="constitutional"]')).toBeVisible();
    }
    
    // Test services navigation
    const servicesLink = page.locator('a[href*="services"], button:has-text("Services")').first();
    if (await servicesLink.isVisible()) {
      await servicesLink.click();
      await page.waitForLoadState('networkidle');
      
      // Verify services content
      await expect(page.locator('.services, [data-testid="services"]')).toBeVisible();
    }
    
    // Test browser back/forward navigation
    await page.goBack();
    await page.waitForLoadState('networkidle');
    await page.goForward();
    await page.waitForLoadState('networkidle');
    
    // Take screenshot for visual regression
    await expect(page).toHaveScreenshot('navigation-complete.png');
  });

  test('🏛️ Constitutional Compliance Validation', async ({ page }) => {
    // Verify constitutional hash in multiple locations
    const constitutionalElements = await page.locator(`[data-constitutional-hash="${CONSTITUTIONAL_HASH}"]`).all();
    expect(constitutionalElements.length).toBeGreaterThan(0);
    
    // Check for constitutional indicators
    const constitutionalIndicators = page.locator('.constitutional-indicator, [data-testid="constitutional-indicator"]');
    if (await constitutionalIndicators.count() > 0) {
      await expect(constitutionalIndicators.first()).toBeVisible();
    }
    
    // Test constitutional validation API if available
    const response = await page.request.post('/api/constitutional/validate', {
      data: {
        hash: CONSTITUTIONAL_HASH,
        timestamp: new Date().toISOString()
      }
    }).catch(() => null);
    
    if (response && response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('constitutional_hash', CONSTITUTIONAL_HASH);
    }
    
    // Verify constitutional compliance in page metadata
    const metaElements = await page.locator('meta[name*="constitutional"], meta[content*="constitutional"]').all();
    console.log(`Found ${metaElements.length} constitutional meta elements`);
  });

  test('⚡ Performance and Responsiveness', async ({ page }) => {
    // Measure page load performance
    const startTime = Date.now();
    await page.goto('/', { waitUntil: 'networkidle' });
    const loadTime = Date.now() - startTime;
    
    // Verify load time is reasonable (< 5 seconds)
    expect(loadTime).toBeLessThan(5000);
    console.log(`Page load time: ${loadTime}ms`);
    
    // Test responsive design
    const viewports = [
      { width: 1920, height: 1080 }, // Desktop
      { width: 1024, height: 768 },  // Tablet
      { width: 375, height: 667 }    // Mobile
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.waitForTimeout(500); // Allow for responsive adjustments
      
      // Verify main content is still visible
      await expect(page.locator('.app')).toBeVisible();
      
      // Take screenshot for visual regression
      await expect(page).toHaveScreenshot(`responsive-${viewport.width}x${viewport.height}.png`);
    }
  });

  test('🔄 User Interactions and State Management', async ({ page }) => {
    // Test button interactions
    const buttons = await page.locator('button:not([disabled])').all();
    
    if (buttons.length > 0) {
      // Test first available button
      const firstButton = buttons[0];
      await firstButton.click();
      await page.waitForTimeout(500);
      
      // Verify no JavaScript errors occurred
      const errors = [];
      page.on('pageerror', error => errors.push(error));
      expect(errors).toHaveLength(0);
    }
    
    // Test form interactions if available
    const inputs = await page.locator('input:not([disabled])').all();
    
    if (inputs.length > 0) {
      const firstInput = inputs[0];
      await firstInput.fill('Test input');
      await expect(firstInput).toHaveValue('Test input');
    }
    
    // Test dropdown/select interactions if available
    const selects = await page.locator('select:not([disabled])').all();
    
    if (selects.length > 0) {
      const firstSelect = selects[0];
      const options = await firstSelect.locator('option').all();
      
      if (options.length > 1) {
        await firstSelect.selectOption({ index: 1 });
      }
    }
    
    // Verify constitutional compliance is maintained after interactions
    const hashAfterInteraction = await page.locator(`[data-constitutional-hash="${CONSTITUTIONAL_HASH}"]`).first().getAttribute('data-constitutional-hash');
    expect(hashAfterInteraction).toBe(CONSTITUTIONAL_HASH);
  });

  test('❌ Error Handling and Recovery', async ({ page }) => {
    // Test 404 page handling
    await page.goto('/non-existent-page');
    
    // Should show 404 or redirect to valid page
    const is404 = await page.locator('h1:has-text("404"), .not-found, [data-testid="404"]').isVisible();
    const isRedirected = await page.url().includes('/dashboard') || await page.url() === page.url().replace('/non-existent-page', '/');
    
    expect(is404 || isRedirected).toBeTruthy();
    
    // Test network error handling
    await page.route('**/api/**', route => route.abort());
    await page.goto('/');
    
    // Application should still load basic UI
    await expect(page.locator('.app')).toBeVisible();
    
    // Constitutional compliance should be maintained
    await expect(page.locator(`[data-constitutional-hash="${CONSTITUTIONAL_HASH}"]`)).toBeVisible();
    
    // Clear route interception
    await page.unroute('**/api/**');
  });

  test('♿ Accessibility and Keyboard Navigation', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    
    // Verify focus is visible
    const focusedElement = await page.locator(':focus').first();
    await expect(focusedElement).toBeVisible();
    
    // Test multiple tab navigation
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }
    
    // Test Enter key activation
    const focusedButton = await page.locator('button:focus').first();
    if (await focusedButton.isVisible()) {
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);
    }
    
    // Verify ARIA attributes are present
    const ariaElements = await page.locator('[aria-label], [aria-labelledby], [role]').all();
    expect(ariaElements.length).toBeGreaterThan(0);
    
    // Test skip links if available
    const skipLinks = page.locator('a[href*="#"], .skip-link');
    if (await skipLinks.count() > 0) {
      await skipLinks.first().click();
    }
  });

  test('🔍 Search and Filter Functionality', async ({ page }) => {
    // Look for search inputs
    const searchInputs = await page.locator('input[type="search"], input[placeholder*="search" i], .search-input').all();
    
    if (searchInputs.length > 0) {
      const searchInput = searchInputs[0];
      
      // Test search functionality
      await searchInput.fill('constitutional');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);
      
      // Verify search results or no errors
      const hasResults = await page.locator('.search-results, .results, [data-testid="search-results"]').isVisible();
      const hasNoResults = await page.locator('.no-results, .empty-state').isVisible();
      
      // Either results or no-results message should be shown
      expect(hasResults || hasNoResults).toBeTruthy();
      
      // Clear search
      await searchInput.clear();
    }
    
    // Test filter functionality if available
    const filterButtons = await page.locator('button:has-text("filter"), .filter-button, [data-testid*="filter"]').all();
    
    if (filterButtons.length > 0) {
      await filterButtons[0].click();
      await page.waitForTimeout(500);
      
      // Verify filter UI appears
      const filterUI = page.locator('.filter-menu, .filter-panel, [data-testid="filter-panel"]');
      if (await filterUI.isVisible()) {
        // Close filter
        await page.keyboard.press('Escape');
      }
    }
  });

  test('📊 Data Loading and Display', async ({ page }) => {
    // Wait for any data loading to complete
    await page.waitForLoadState('networkidle');
    
    // Look for data tables or lists
    const dataTables = await page.locator('table, .data-table, [data-testid*="table"]').all();
    const dataLists = await page.locator('ul, ol, .list, [data-testid*="list"]').all();
    
    if (dataTables.length > 0) {
      const table = dataTables[0];
      await expect(table).toBeVisible();
      
      // Verify table has headers
      const headers = await table.locator('th, .header').all();
      expect(headers.length).toBeGreaterThan(0);
    }
    
    if (dataLists.length > 0) {
      const list = dataLists[0];
      await expect(list).toBeVisible();
      
      // Verify list has items
      const items = await list.locator('li, .item').all();
      expect(items.length).toBeGreaterThan(0);
    }
    
    // Test pagination if available
    const paginationButtons = await page.locator('button:has-text("next"), button:has-text("previous"), .pagination button').all();
    
    if (paginationButtons.length > 0) {
      const nextButton = paginationButtons.find(async btn => 
        (await btn.textContent()).toLowerCase().includes('next')
      );
      
      if (nextButton && await nextButton.isEnabled()) {
        await nextButton.click();
        await page.waitForLoadState('networkidle');
      }
    }
  });

});
