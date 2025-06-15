# Comprehensive Testing Strategy

## Testing Overview ✅

The governance dashboard implements a multi-layered testing approach ensuring 95%+ code coverage, WCAG 2.1 accessibility compliance, and optimal performance across all user scenarios.

## Testing Pyramid Structure

### Unit Tests (90%+ Coverage) ✅
**Framework**: Jest + React Testing Library + TypeScript
**Coverage Target**: 95%
**Focus**: Individual component behavior and utility functions

#### Component Testing Examples
```typescript
// DashboardCard unit tests
describe('DashboardCard Component', () => {
  const mockCard: DashboardCardData = {
    id: 'test-metric',
    title: 'Active Users',
    variant: 'metric',
    size: 'small',
    position: 0,
    data: {
      value: 1247,
      label: 'Currently online',
      format: 'number',
      change: { direction: 'up', percentage: 8.2, period: 'this week' }
    }
  };

  it('renders metric data with correct formatting', () => {
    render(<DashboardCard card={mockCard} />);
    
    expect(screen.getByText('Active Users')).toBeInTheDocument();
    expect(screen.getByText('1,247')).toBeInTheDocument();
    expect(screen.getByText('Currently online')).toBeInTheDocument();
    expect(screen.getByText('8.2%')).toBeInTheDocument();
    expect(screen.getByText('this week')).toBeInTheDocument();
  });

  it('handles different value formats correctly', () => {
    const percentageCard = {
      ...mockCard,
      data: { ...mockCard.data, value: 85.5, format: 'percentage' }
    };
    
    render(<DashboardCard card={percentageCard} />);
    expect(screen.getByText('85.5%')).toBeInTheDocument();
  });

  it('provides proper loading state during refresh', async () => {
    const onRefresh = jest.fn(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(<DashboardCard card={mockCard} onRefresh={onRefresh} />);
    
    const refreshButton = screen.getByLabelText('Refresh Active Users');
    await userEvent.click(refreshButton);
    
    expect(refreshButton).toBeDisabled();
    expect(screen.getByTestId('refresh-spinner')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(refreshButton).not.toBeDisabled();
    });
  });

  it('handles error states gracefully', () => {
    const errorCard = { ...mockCard, data: null };
    
    render(<DashboardCard card={errorCard} />);
    
    expect(screen.getByText('Failed to load card content')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });
});

// PolicyFilters unit tests
describe('PolicyFilters Component', () => {
  const mockProps = {
    onFiltersChange: jest.fn(),
    totalCount: 100,
    filteredCount: 50
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('debounces search input correctly', async () => {
    render(<PolicyFilters {...mockProps} />);
    
    const searchInput = screen.getByPlaceholderText(/Search policies/);
    await userEvent.type(searchInput, 'test query');
    
    // Should not call immediately
    expect(mockProps.onFiltersChange).not.toHaveBeenCalled();
    
    // Should call after debounce delay
    await waitFor(() => {
      expect(mockProps.onFiltersChange).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'test query' })
      );
    }, { timeout: 500 });
  });

  it('synchronizes filter state with URL parameters', async () => {
    const mockReplace = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({ replace: mockReplace });
    
    render(<PolicyFilters {...mockProps} />);
    
    // Select a category filter
    const privacyFilter = screen.getByText('Privacy');
    await userEvent.click(privacyFilter);
    
    expect(mockReplace).toHaveBeenCalledWith(
      expect.stringContaining('category=Privacy'),
      expect.any(Object)
    );
  });

  it('clears all filters when clear button is clicked', async () => {
    // Mock initial state with filters
    const searchParams = new URLSearchParams('search=test&category=Privacy');
    (useSearchParams as jest.Mock).mockReturnValue(searchParams);
    
    render(<PolicyFilters {...mockProps} />);
    
    const clearButton = screen.getByText('Clear');
    await userEvent.click(clearButton);
    
    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      search: '',
      categories: [],
      status: [],
      dateRange: { start: null, end: null },
      sortBy: 'updatedAt',
      sortOrder: 'desc'
    });
  });
});
```

#### Utility Function Testing
```typescript
// Utility function tests
describe('Utility Functions', () => {
  describe('formatDate', () => {
    it('formats dates correctly', () => {
      const date = new Date('2024-01-15');
      expect(formatDate(date)).toBe('January 15, 2024');
    });

    it('handles invalid dates gracefully', () => {
      expect(formatDate(new Date('invalid'))).toBe('Invalid date');
    });
  });

  describe('debounce', () => {
    it('delays function execution', async () => {
      const mockFn = jest.fn();
      const debouncedFn = debounce(mockFn, 100);
      
      debouncedFn('test1');
      debouncedFn('test2');
      debouncedFn('test3');
      
      expect(mockFn).not.toHaveBeenCalled();
      
      await new Promise(resolve => setTimeout(resolve, 150));
      
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenCalledWith('test3');
    });
  });
});
```

### Integration Tests ✅
**Framework**: React Testing Library + MSW (Mock Service Worker)
**Focus**: Component interactions, API integration, workflow testing

#### Component Integration Testing
```typescript
// Dashboard integration tests
describe('Dashboard Integration', () => {
  it('loads and displays dashboard data correctly', async () => {
    // Mock API responses
    server.use(
      rest.get('/api/dashboard/metrics', (req, res, ctx) => {
        return res(ctx.json({
          metrics: [
            { id: '1', title: 'Active Policies', value: 24 },
            { id: '2', title: 'Pending Proposals', value: 8 }
          ]
        }));
      })
    );

    render(<DashboardPage />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Active Policies')).toBeInTheDocument();
      expect(screen.getByText('24')).toBeInTheDocument();
      expect(screen.getByText('Pending Proposals')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    server.use(
      rest.get('/api/dashboard/metrics', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to load dashboard data/)).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });
});

// Policy workflow integration tests
describe('Policy Management Workflow', () => {
  it('completes policy creation workflow', async () => {
    const mockCreatePolicy = jest.fn().mockResolvedValue({
      id: 'new-policy',
      title: 'Test Policy',
      status: 'draft'
    });

    render(<PolicyManagementPage />);
    
    // Click create button
    await userEvent.click(screen.getByText('New Policy'));
    
    // Fill form
    await userEvent.type(screen.getByLabelText('Policy Title'), 'Test Policy');
    await userEvent.type(screen.getByLabelText('Description'), 'Test description');
    await userEvent.selectOptions(screen.getByLabelText('Category'), 'Security');
    
    // Submit
    await userEvent.click(screen.getByText('Create Policy'));
    
    await waitFor(() => {
      expect(screen.getByText('Policy created successfully')).toBeInTheDocument();
    });
  });

  it('validates form inputs before submission', async () => {
    render(<PolicyCreationForm />);
    
    // Try to submit empty form
    await userEvent.click(screen.getByText('Create Policy'));
    
    expect(screen.getByText('Title is required')).toBeInTheDocument();
    expect(screen.getByText('Description is required')).toBeInTheDocument();
  });
});
```

### End-to-End Tests ✅
**Framework**: Playwright
**Focus**: Complete user journeys, cross-browser compatibility, performance validation

#### E2E Test Scenarios
```typescript
// Critical user flow tests
import { test, expect } from '@playwright/test';

test.describe('Governance Dashboard E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Login flow
    await page.click('[data-testid="login-button"]');
    await page.fill('[data-testid="username"]', 'testuser');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="submit-login"]');
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
  });

  test('should navigate through all main sections', async ({ page }) => {
    // Test navigation
    await page.click('[data-testid="nav-policies"]');
    await expect(page).toHaveURL('/policies');
    await expect(page.locator('h1')).toContainText('Policies');
    
    await page.click('[data-testid="nav-governance"]');
    await expect(page).toHaveURL('/governance');
    await expect(page.locator('h1')).toContainText('Governance');
    
    await page.click('[data-testid="nav-dashboard"]');
    await expect(page).toHaveURL('/');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should complete constitutional amendment workflow', async ({ page }) => {
    await page.goto('/constitutional-amendment');
    
    // Step 1: Select principle
    await page.click('[data-testid="principle-PC-001"]');
    
    // Step 2: Propose amendment
    await page.fill('[data-testid="proposed-content"]', 'Updated principle content...');
    await page.fill('[data-testid="rationale"]', 'This update improves clarity...');
    await page.click('[data-testid="submit-amendment"]');
    
    // Wait for analysis
    await expect(page.locator('[data-testid="gs-analysis"]')).toBeVisible();
    await expect(page.locator('[data-testid="pgc-validation"]')).toBeVisible();
    
    // Step 3: Voting
    await expect(page.locator('[data-testid="voting-interface"]')).toBeVisible();
    await page.click('[data-testid="vote-for"]');
    
    await expect(page.locator('[data-testid="vote-success"]')).toBeVisible();
  });

  test('should handle policy filtering correctly', async ({ page }) => {
    await page.goto('/policies');
    
    // Test search
    await page.fill('[data-testid="search-input"]', 'security');
    await page.waitForTimeout(500); // Wait for debounce
    
    const policyCards = page.locator('[data-testid="policy-card"]');
    const count = await policyCards.count();
    expect(count).toBeGreaterThan(0);
    
    // Verify search results
    for (let i = 0; i < count; i++) {
      const card = policyCards.nth(i);
      const text = await card.textContent();
      expect(text?.toLowerCase()).toContain('security');
    }
    
    // Test category filter
    await page.click('[data-testid="filters-button"]');
    await page.click('[data-testid="category-privacy"]');
    
    await page.waitForSelector('[data-testid="policy-card"]');
    const filteredCards = page.locator('[data-testid="policy-card"]');
    const filteredCount = await filteredCards.count();
    
    for (let i = 0; i < filteredCount; i++) {
      const category = await filteredCards.nth(i).locator('[data-testid="policy-category"]').textContent();
      expect(category).toBe('Privacy');
    }
  });

  test('should maintain state across page refreshes', async ({ page }) => {
    await page.goto('/policies?search=data&category=Privacy&status=active');
    
    // Verify initial state
    expect(await page.inputValue('[data-testid="search-input"]')).toBe('data');
    expect(await page.locator('[data-testid="category-privacy"]').getAttribute('aria-pressed')).toBe('true');
    
    // Refresh page
    await page.reload();
    
    // Verify state persisted
    expect(await page.inputValue('[data-testid="search-input"]')).toBe('data');
    expect(await page.locator('[data-testid="category-privacy"]').getAttribute('aria-pressed')).toBe('true');
  });
});

// Performance testing
test.describe('Performance Tests', () => {
  test('should meet Core Web Vitals targets', async ({ page }) => {
    await page.goto('/');
    
    // Measure LCP
    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      });
    });
    
    expect(lcp).toBeLessThan(2500); // LCP < 2.5s
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    // Navigate to policies page with large dataset
    await page.goto('/policies?limit=1000');
    
    const startTime = Date.now();
    await page.waitForSelector('[data-testid="policy-card"]');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000); // Load within 3 seconds
    
    // Test scrolling performance
    const scrollStart = Date.now();
    await page.mouse.wheel(0, 5000);
    await page.waitForTimeout(100);
    const scrollTime = Date.now() - scrollStart;
    
    expect(scrollTime).toBeLessThan(500); // Smooth scrolling
  });
});
```

### Accessibility Testing ✅
**Framework**: jest-axe + Manual testing with screen readers
**Focus**: WCAG 2.1 AA compliance, screen reader compatibility, keyboard navigation

#### Automated Accessibility Testing
```typescript
// Accessibility testing with jest-axe
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  it('should not have accessibility violations on dashboard', async () => {
    const { container } = render(<DashboardPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should not have accessibility violations on policy cards', async () => {
    const { container } = render(<PolicyCard policy={mockPolicy} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should provide proper focus management in modals', async () => {
    render(<PolicyEditModal policy={mockPolicy} isOpen={true} />);
    
    // Modal should receive focus when opened
    const modal = screen.getByRole('dialog');
    expect(modal).toHaveFocus();
    
    // Escape key should close modal
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('should support keyboard navigation in dropdown menus', async () => {
    render(<PolicyCard policy={mockPolicy} />);
    
    const menuButton = screen.getByLabelText(/More actions/);
    
    // Open menu with Enter key
    menuButton.focus();
    await userEvent.keyboard('{Enter}');
    
    // Navigate with arrow keys
    await userEvent.keyboard('{ArrowDown}');
    expect(screen.getByText('Edit Policy')).toHaveFocus();
    
    await userEvent.keyboard('{ArrowDown}');
    expect(screen.getByText('Delete Policy')).toHaveFocus();
    
    // Activate with Enter
    await userEvent.keyboard('{Enter}');
    expect(mockOnEdit).toHaveBeenCalled();
  });
});
```

#### Screen Reader Testing Protocol
```typescript
// Screen reader testing scenarios
describe('Screen Reader Compatibility', () => {
  it('announces dynamic content changes', async () => {
    render(<DashboardCard card={mockCard} />);
    
    // Simulate data update
    const updatedCard = { ...mockCard, data: { ...mockCard.data, value: 1500 } };
    rerender(<DashboardCard card={updatedCard} />);
    
    // Check for live region announcement
    expect(screen.getByRole('status')).toHaveTextContent('Value updated to 1,500');
  });

  it('provides meaningful context for complex widgets', () => {
    render(<PolicyFilters {...mockProps} />);
    
    // Check for proper labeling
    expect(screen.getByLabelText('Search policies')).toBeInTheDocument();
    expect(screen.getByRole('group', { name: 'Filter options' })).toBeInTheDocument();
    
    // Check for status announcements
    const filterButton = screen.getByText('Privacy');
    filterButton.click();
    
    expect(screen.getByRole('status')).toHaveTextContent('Privacy filter applied');
  });
});
```

### Performance Testing ✅
**Framework**: Lighthouse CI + k6 + Custom monitoring
**Focus**: Core Web Vitals, load testing, memory usage

#### Lighthouse CI Configuration
```javascript
// lighthouse.config.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/policies',
        'http://localhost:3000/governance',
        'http://localhost:3000/constitutional-amendment'
      ],
      startServerCommand: 'npm run start',
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
        
        // Specific metrics
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'first-input-delay': ['error', { maxNumericValue: 100 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

#### Load Testing with k6
```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Error rate under 1%
  },
};

export default function () {
  // Test dashboard page
  let response = http.get('http://localhost:3000/');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'contains dashboard content': (r) => r.body.includes('Dashboard'),
  });

  sleep(1);

  // Test policies page
  response = http.get('http://localhost:3000/policies');
  check(response, {
    'policies page loads': (r) => r.status === 200,
    'response time < 1s': (r) => r.timings.duration < 1000,
  });

  sleep(1);
  
  // Test search functionality
  response = http.get('http://localhost:3000/policies?search=security');
  check(response, {
    'search results load': (r) => r.status === 200,
    'search response time < 750ms': (r) => r.timings.duration < 750,
  });

  sleep(2);
}
```

### Visual Regression Testing ✅
**Framework**: Chromatic + Percy
**Focus**: UI consistency, cross-browser compatibility

```typescript
// Visual regression test setup
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('dashboard page visual consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveScreenshot('dashboard-page.png');
  });

  test('policy card variations', async ({ page }) => {
    await page.goto('/policies');
    
    // Test different policy states
    const activeCard = page.locator('[data-testid="policy-card-active"]').first();
    await expect(activeCard).toHaveScreenshot('policy-card-active.png');
    
    const draftCard = page.locator('[data-testid="policy-card-draft"]').first();
    await expect(draftCard).toHaveScreenshot('policy-card-draft.png');
  });

  test('dark mode consistency', async ({ page }) => {
    // Enable dark mode
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.goto('/');
    
    await expect(page).toHaveScreenshot('dashboard-dark-mode.png');
  });
});
```

## Continuous Integration Pipeline ✅

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3

  accessibility-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:a11y
      - uses: Pa11y/pa11y-ci-action@v1

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install
      - run: npm run test:e2e

  lighthouse-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - run: npm run lhci:autorun

  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: chromaui/action@v1
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

## Test Coverage Requirements ✅

### Coverage Metrics
- **Unit Tests**: 95% line coverage, 90% branch coverage
- **Integration Tests**: 100% critical user flows
- **E2E Tests**: 100% key user journeys
- **Accessibility**: Zero violations in automated tests
- **Performance**: All pages meet Core Web Vitals targets

### Quality Gates
- All tests must pass before merge
- Coverage thresholds must be met
- No accessibility violations allowed
- Performance budgets must be respected
- Visual regression tests must pass

This comprehensive testing strategy ensures the governance dashboard maintains the highest quality standards while providing an excellent user experience across all scenarios and devices.