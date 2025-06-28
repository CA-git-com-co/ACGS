import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '@/components/ui/button';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe('Button Accessibility Tests', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be focusable with keyboard', async () => {
    const user = userEvent.setup();
    render(<Button>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });

    // Button should be focusable
    await user.tab();
    expect(button).toHaveFocus();
  });

  it('should have proper ARIA attributes when disabled', async () => {
    render(<Button disabled>Disabled Button</Button>);

    const button = screen.getByRole('button', { name: /disabled button/i });
    expect(button).toBeDisabled();
    // HTML disabled attribute is sufficient for buttons
    expect(button).toHaveAttribute('disabled');
  });

  it('should support keyboard activation', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<Button onClick={handleClick}>Clickable</Button>);

    const button = screen.getByRole('button', { name: /clickable/i });

    // Focus and activate with Enter
    button.focus();
    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalledTimes(1);

    // Activate with Space
    await user.keyboard(' ');
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('should have proper contrast for all variants', async () => {
    const variants = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'] as const;

    for (const variant of variants) {
      const { container } = render(<Button variant={variant}>Test Button</Button>);
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true },
        },
      });
      expect(results).toHaveNoViolations();
    }
  });

  it('should have appropriate focus indicators', () => {
    render(<Button>Focus me</Button>);

    const button = screen.getByRole('button', { name: /focus me/i });

    // Check that focus styles are properly applied
    expect(button).toHaveClass('focus-visible:ring-2');
    expect(button).toHaveClass('focus-visible:ring-ring');
  });

  it('should work with asChild prop and maintain accessibility', async () => {
    const { container } = render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    // Should render as a link but maintain button styles
    const link = screen.getByRole('link', { name: /link button/i });
    expect(link).toBeInTheDocument();
  });
});
