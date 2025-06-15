import { test, expect } from '@playwright/test';

/**
 * E2E tests for ACGS-PGP Framework governance workflows
 * 
 * Tests the complete constitutional governance process including
 * principle management, policy synthesis, and compliance validation.
 */

test.describe('ACGS Constitutional Governance Workflows', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Storybook
    await page.goto('/');
    
    // Wait for Storybook to load
    await page.waitForSelector('[data-testid="storybook-explorer-tree"]');
  });

  test.describe('ComplianceChecker Component', () => {
    test('should render compliance checker interface', async ({ page }) => {
      // Navigate to ComplianceChecker story
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Default');

      // Wait for component to load
      await page.waitForSelector('iframe[title="storybook-preview-iframe"]');
      
      // Switch to iframe
      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify main elements are present
      await expect(iframe.locator('text=🔍 PGC Compliance Checker')).toBeVisible();
      await expect(iframe.locator('label:has-text("Action to Check")')).toBeVisible();
      await expect(iframe.locator('label:has-text("Select Policy")')).toBeVisible();
      await expect(iframe.locator('button:has-text("Check Compliance")')).toBeVisible();
    });

    test('should perform compliance validation workflow', async ({ page }) => {
      // Navigate to ComplianceChecker interactive demo
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Interactive Demo');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Fill out the compliance form
      await iframe.locator('input[placeholder*="action"]').fill('Transfer 500 tokens to treasury');
      await iframe.locator('select').selectOption({ index: 1 }); // Select first policy
      
      // Set context
      await iframe.locator('input[type="checkbox"]').first().check(); // Requires governance
      await iframe.locator('input[type="number"]').fill('500');
      
      // Submit compliance check
      await iframe.locator('button:has-text("Check Compliance")').click();
      
      // Verify compliance result appears
      await expect(iframe.locator('text=Recent Compliance Results')).toBeVisible({ timeout: 10000 });
    });

    test('should handle compliance violations', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Interactive Demo');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Enter an action that should violate policy
      await iframe.locator('input[placeholder*="action"]').fill('unauthorized system access violation');
      await iframe.locator('select').selectOption({ index: 1 });
      
      // Submit compliance check
      await iframe.locator('button:has-text("Check Compliance")').click();
      
      // Should still show results (mock will handle violation logic)
      await expect(iframe.locator('text=Recent Compliance Results')).toBeVisible({ timeout: 10000 });
    });

    test('should validate form requirements', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Default');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Button should be disabled initially
      await expect(iframe.locator('button:has-text("Check Compliance")')).toBeDisabled();
      
      // Fill action only
      await iframe.locator('input[placeholder*="action"]').fill('Test action');
      await expect(iframe.locator('button:has-text("Check Compliance")')).toBeDisabled();
      
      // Select policy
      await iframe.locator('select').selectOption({ index: 1 });
      await expect(iframe.locator('button:has-text("Check Compliance")')).toBeEnabled();
    });
  });

  test.describe('PolicyCard Component', () => {
    test('should render policy information correctly', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Policy');
      await page.click('text=PolicyCard');
      await page.click('text=Active Policy');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify policy card elements
      await expect(iframe.locator('text=Treasury Protection Policy')).toBeVisible();
      await expect(iframe.locator('text=ACTIVE')).toBeVisible();
      await expect(iframe.locator('text=Validation Score')).toBeVisible();
      await expect(iframe.locator('text=Complexity')).toBeVisible();
      await expect(iframe.locator('text=Rules')).toBeVisible();
    });

    test('should handle policy actions', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Policy');
      await page.click('text=PolicyCard');
      await page.click('text=Interactive Demo');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Test edit action
      await iframe.locator('button:has-text("Edit")').first().click();
      
      // Test activate action on draft policy
      await iframe.locator('button:has-text("Activate")').click();
      
      // Test deactivate action on active policy
      await iframe.locator('button:has-text("Deactivate")').click();
    });

    test('should display policy rules correctly', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Policy');
      await page.click('text=PolicyCard');
      await page.click('text=Complex Policy');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify rules section
      await expect(iframe.locator('text=Rules')).toBeVisible();
      await expect(iframe.locator('text=Condition:')).toBeVisible();
      await expect(iframe.locator('text=Action:')).toBeVisible();
    });
  });

  test.describe('Loading States', () => {
    test('should display various loading components', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Loading');
      await page.click('text=Spinner');
      await page.click('text=All Colors');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify multiple spinners are visible
      const spinners = iframe.locator('[role="status"]');
      await expect(spinners).toHaveCount(6); // All color variants
    });

    test('should show progress indicators', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Loading');
      await page.click('text=Progress');
      await page.click('text=Progress Colors');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify progress bars
      await expect(iframe.locator('[role="progressbar"]')).toHaveCount(5);
      await expect(iframe.locator('text=AC Service Connection')).toBeVisible();
      await expect(iframe.locator('text=GS Policy Synthesis')).toBeVisible();
      await expect(iframe.locator('text=PGC Compliance Check')).toBeVisible();
    });

    test('should demonstrate loading button states', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Loading');
      await page.click('text=LoadingButton');
      await page.click('text=Loading Button Active');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify loading button shows loading state
      await expect(iframe.locator('text=Creating principle...')).toBeVisible();
      await expect(iframe.locator('button')).toBeDisabled();
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper ARIA labels and roles', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Default');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Check form accessibility
      await expect(iframe.locator('label[for]')).toHaveCount(5); // All form labels
      await expect(iframe.locator('input[aria-describedby]')).toHaveCount(2); // Inputs with descriptions
      await expect(iframe.locator('button[type="submit"]')).toHaveCount(1); // Submit button
    });

    test('should support keyboard navigation', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Default');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Test tab navigation
      await iframe.locator('input').first().focus();
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to reach submit button
      await expect(iframe.locator('button:has-text("Check Compliance")')).toBeFocused();
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Responsive Demo');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify mobile layout
      await expect(iframe.locator('text=Mobile Size')).toBeVisible();
      await expect(iframe.locator('text=🔍 PGC Compliance Checker')).toBeVisible();
    });

    test('should adapt to tablet size', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await page.click('text=Components');
      await page.click('text=Policy');
      await page.click('text=PolicyCard');
      await page.click('text=Policy Grid');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify grid layout adapts
      await expect(iframe.locator('.policy-card')).toHaveCount(4);
    });
  });

  test.describe('Error Handling', () => {
    test('should display error states gracefully', async ({ page }) => {
      await page.click('text=Components');
      await page.click('text=Governance');
      await page.click('text=ComplianceChecker');
      await page.click('text=Error Handling');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify error handling demo
      await expect(iframe.locator('text=⚠️ Error Handling Demo')).toBeVisible();
      await expect(iframe.locator('text=Service errors would be caught and displayed gracefully')).toBeVisible();
    });
  });

  test.describe('Cross-Browser Compatibility', () => {
    test('should work consistently across browsers', async ({ page, browserName }) => {
      await page.click('text=Components');
      await page.click('text=Loading');
      await page.click('text=Spinner');
      await page.click('text=Default');

      const iframe = page.frameLocator('iframe[title="storybook-preview-iframe"]');
      
      // Verify spinner renders in all browsers
      await expect(iframe.locator('[role="status"]')).toBeVisible();
      
      // Log browser for debugging
      console.log(`✅ Spinner component working in ${browserName}`);
    });
  });
});
