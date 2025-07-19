// ACGS-2 Visual Regression E2E Tests
// Constitutional Hash: cdd01ef066bc6cf2
// 
// Comprehensive visual regression testing for UI consistency

const { test, expect } = require('@playwright/test');

const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2';

test.describe('📸 Visual Regression Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Verify constitutional compliance
    const constitutionalElement = await page.locator('[data-constitutional-hash]').first();
    const hashValue = await constitutionalElement.getAttribute('data-constitutional-hash');
    expect(hashValue).toBe(CONSTITUTIONAL_HASH);
  });

  test('🎨 Component Visual Consistency', async ({ page }) => {
    // Test main layout visual consistency
    await expect(page.locator('.app')).toHaveScreenshot('main-layout.png');
    
    // Test navigation visual consistency
    const navigation = page.locator('nav, .navigation, [role="navigation"]').first();
    if (await navigation.isVisible()) {
      await expect(navigation).toHaveScreenshot('navigation-component.png');
    }
    
    // Test dashboard visual consistency
    const dashboardLink = page.locator('a[href*="dashboard"], button:has-text("Dashboard")').first();
    if (await dashboardLink.isVisible()) {
      await dashboardLink.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.dashboard, main')).toHaveScreenshot('dashboard-layout.png');
    }
    
    // Test constitutional section visual consistency
    const constitutionalLink = page.locator('a[href*="constitutional"], button:has-text("Constitutional")').first();
    if (await constitutionalLink.isVisible()) {
      await constitutionalLink.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.constitutional, main')).toHaveScreenshot('constitutional-layout.png');
    }
  });
  
  test('📱 Responsive Visual Testing', async ({ page }) => {
    const viewports = [
      { name: 'desktop', width: 1920, height: 1080 },
      { name: 'laptop', width: 1366, height: 768 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'mobile', width: 375, height: 667 }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Take full page screenshot
      await expect(page).toHaveScreenshot(`responsive-${viewport.name}-full.png`, {
        fullPage: true
      });
      
      // Test specific components at this viewport
      const mainContent = page.locator('main, .app').first();
      await expect(mainContent).toHaveScreenshot(`responsive-${viewport.name}-main.png`);
    }
  });
  
  test('🎭 Interactive State Visual Testing', async ({ page }) => {
    // Test button hover states
    const buttons = await page.locator('button:not([disabled])').all();
    if (buttons.length > 0) {
      await buttons[0].hover();
      await expect(buttons[0]).toHaveScreenshot('button-hover-state.png');
    }
    
    // Test focus states
    const focusableElements = await page.locator('button, a, input, select').all();
    if (focusableElements.length > 0) {
      await focusableElements[0].focus();
      await expect(focusableElements[0]).toHaveScreenshot('element-focus-state.png');
    }
    
    // Test loading states if available
    const loadingElements = page.locator('.loading, .spinner, [data-testid*="loading"]');
    if (await loadingElements.count() > 0) {
      await expect(loadingElements.first()).toHaveScreenshot('loading-state.png');
    }
    
    // Test error states if available
    const errorElements = page.locator('.error, .alert, [data-testid*="error"]');
    if (await errorElements.count() > 0) {
      await expect(errorElements.first()).toHaveScreenshot('error-state.png');
    }
  });
  
  test('🌈 Theme and Color Consistency', async ({ page }) => {
    // Test light theme (default)
    await expect(page).toHaveScreenshot('theme-light.png');
    
    // Test dark theme if available
    const themeToggle = page.locator('button:has-text("dark"), .theme-toggle, [data-testid*="theme"]').first();
    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      await page.waitForTimeout(500); // Allow theme transition
      await expect(page).toHaveScreenshot('theme-dark.png');
    }
    
    // Test high contrast mode if available
    const contrastToggle = page.locator('button:has-text("contrast"), .contrast-toggle').first();
    if (await contrastToggle.isVisible()) {
      await contrastToggle.click();
      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('theme-high-contrast.png');
    }
  });
  
  test('📊 Data Visualization Consistency', async ({ page }) => {
    // Look for charts, graphs, or data visualizations
    const charts = await page.locator('canvas, svg, .chart, [data-testid*="chart"]').all();
    
    if (charts.length > 0) {
      for (let i = 0; i < Math.min(charts.length, 3); i++) {
        const chart = charts[i];
        if (await chart.isVisible()) {
          await expect(chart).toHaveScreenshot(`chart-${i + 1}.png`);
        }
      }
    }
    
    // Test tables visual consistency
    const tables = await page.locator('table, .data-table').all();
    
    if (tables.length > 0) {
      const table = tables[0];
      await expect(table).toHaveScreenshot('data-table.png');
    }
    
    // Test cards or panels
    const cards = await page.locator('.card, .panel, .widget').all();
    
    if (cards.length > 0) {
      const card = cards[0];
      await expect(card).toHaveScreenshot('card-component.png');
    }
  });
  
  test('🔄 Animation and Transition Consistency', async ({ page }) => {
    // Test modal animations if available
    const modalTrigger = page.locator('button:has-text("modal"), .modal-trigger').first();
    if (await modalTrigger.isVisible()) {
      await modalTrigger.click();
      await page.waitForTimeout(300); // Wait for animation
      
      const modal = page.locator('.modal, [role="dialog"]').first();
      if (await modal.isVisible()) {
        await expect(modal).toHaveScreenshot('modal-open.png');
        
        // Close modal
        const closeButton = modal.locator('button:has-text("close"), .close-button').first();
        if (await closeButton.isVisible()) {
          await closeButton.click();
        } else {
          await page.keyboard.press('Escape');
        }
      }
    }
    
    // Test dropdown animations if available
    const dropdownTrigger = page.locator('button:has-text("menu"), .dropdown-trigger').first();
    if (await dropdownTrigger.isVisible()) {
      await dropdownTrigger.click();
      await page.waitForTimeout(200);
      
      const dropdown = page.locator('.dropdown, .menu').first();
      if (await dropdown.isVisible()) {
        await expect(dropdown).toHaveScreenshot('dropdown-open.png');
      }
    }
    
    // Test tab transitions if available
    const tabs = await page.locator('.tab, [role="tab"]').all();
    if (tabs.length > 1) {
      await tabs[1].click();
      await page.waitForTimeout(200);
      await expect(page.locator('.tab-content, [role="tabpanel"]')).toHaveScreenshot('tab-transition.png');
    }
  });
  
  test('🏛️ Constitutional Compliance Visual Elements', async ({ page }) => {
    // Test constitutional indicators
    const constitutionalIndicators = page.locator('.constitutional-indicator, [data-testid="constitutional-indicator"]');
    if (await constitutionalIndicators.count() > 0) {
      await expect(constitutionalIndicators.first()).toHaveScreenshot('constitutional-indicator.png');
    }
    
    // Test compliance badges or status elements
    const complianceBadges = page.locator('.compliance-badge, .status-badge, [data-testid*="compliance"]');
    if (await complianceBadges.count() > 0) {
      await expect(complianceBadges.first()).toHaveScreenshot('compliance-badge.png');
    }
    
    // Test governance-related UI elements
    const governanceElements = page.locator('.governance, [data-testid*="governance"]');
    if (await governanceElements.count() > 0) {
      await expect(governanceElements.first()).toHaveScreenshot('governance-element.png');
    }
    
    // Verify constitutional hash is visually consistent
    const hashElements = await page.locator(`[data-constitutional-hash="${CONSTITUTIONAL_HASH}"]`).all();
    expect(hashElements.length).toBeGreaterThan(0);
    
    // Take screenshot of page with constitutional elements highlighted
    await page.addStyleTag({
      content: `
        [data-constitutional-hash="${CONSTITUTIONAL_HASH}"] {
          outline: 2px solid #00ff00 !important;
          outline-offset: 2px !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('constitutional-elements-highlighted.png');
  });
  
  test('📐 Layout and Spacing Consistency', async ({ page }) => {
    // Test grid layouts
    const gridContainers = page.locator('.grid, .grid-container, [style*="grid"]');
    if (await gridContainers.count() > 0) {
      await expect(gridContainers.first()).toHaveScreenshot('grid-layout.png');
    }
    
    // Test flex layouts
    const flexContainers = page.locator('.flex, .flex-container, [style*="flex"]');
    if (await flexContainers.count() > 0) {
      await expect(flexContainers.first()).toHaveScreenshot('flex-layout.png');
    }
    
    // Test spacing consistency by highlighting margins and padding
    await page.addStyleTag({
      content: `
        * {
          box-shadow: inset 0 0 0 1px rgba(255, 0, 0, 0.1) !important;
        }
        *:hover {
          box-shadow: inset 0 0 0 2px rgba(255, 0, 0, 0.3) !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('layout-spacing-debug.png');
  });
  
});
