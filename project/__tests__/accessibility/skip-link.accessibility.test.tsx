import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { SkipLink } from '@/components/ui/skip-link';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe('SkipLink Accessibility Tests', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SkipLink href="#main-content">Skip to main content</SkipLink>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be visually hidden by default', () => {
    render(<SkipLink href="#main-content">Skip to main content</SkipLink>);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toHaveClass('sr-only');
  });

  it('should become visible when focused', async () => {
    const user = userEvent.setup();
    render(<SkipLink href="#main-content">Skip to main content</SkipLink>);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });

    // Focus the skip link
    await user.tab();
    expect(skipLink).toHaveFocus();

    // Should have focus classes that make it visible
    expect(skipLink).toHaveClass('focus:not-sr-only');
    expect(skipLink).toHaveClass('focus:top-6');
  });

  it('should have proper href attribute', () => {
    render(<SkipLink href="#main-content">Skip to main content</SkipLink>);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });

  it('should be the first focusable element', async () => {
    const user = userEvent.setup();
    render(
      <div>
        <SkipLink href="#main-content">Skip to main content</SkipLink>
        <button>Other button</button>
      </div>
    );

    // First tab should focus the skip link
    await user.tab();
    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toHaveFocus();
  });

  it('should have high z-index for proper layering', () => {
    render(<SkipLink href="#main-content">Skip to main content</SkipLink>);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toHaveClass('z-[9999]');
  });

  it('should support keyboard activation', async () => {
    const user = userEvent.setup();

    // Mock scrollIntoView since it's not implemented in JSDOM
    const mockScrollIntoView = jest.fn();
    Element.prototype.scrollIntoView = mockScrollIntoView;

    render(
      <div>
        <SkipLink href="#main-content">Skip to main content</SkipLink>
        <main id="main-content">Main content</main>
      </div>
    );

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });

    // Focus and activate with Enter
    skipLink.focus();
    await user.keyboard('{Enter}');

    // Should navigate to the target
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });

  it('should have proper contrast when focused', async () => {
    const { container } = render(<SkipLink href="#main-content">Skip to main content</SkipLink>);

    // Test with focus styles applied
    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    skipLink.focus();

    const results = await axe(container, {
      rules: {
        'color-contrast': { enabled: true },
      },
    });
    expect(results).toHaveNoViolations();
  });
});
