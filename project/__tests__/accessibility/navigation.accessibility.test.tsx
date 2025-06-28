import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Navigation } from '@/components/navigation/Navigation';

// Mock next-auth
jest.mock('next-auth/react', () => ({
  useSession: () => ({
    data: {
      user: {
        name: 'John Doe',
        email: 'john@example.com',
      },
    },
  }),
  signOut: jest.fn(),
}));

// Extend Jest matchers
expect.extend(toHaveNoViolations);

describe('Navigation Accessibility Tests', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Navigation />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper landmark roles', () => {
    render(<Navigation />);

    // Header should have banner role
    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();

    // Navigation should be properly labeled
    const nav = screen.getByRole('navigation', { name: /user account navigation/i });
    expect(nav).toBeInTheDocument();
  });

  it('should have proper heading hierarchy', () => {
    render(<Navigation />);

    // Main heading should be h1
    const heading = screen.getByRole('heading', { level: 1, name: /acgs/i });
    expect(heading).toBeInTheDocument();
  });

  it('should have accessible user menu button', () => {
    render(<Navigation />);

    // User menu button should have proper aria-label
    const menuButton = screen.getByRole('button', { name: /open user menu for john doe/i });
    expect(menuButton).toBeInTheDocument();
    expect(menuButton).toHaveAttribute('aria-label');
  });

  it('should have proper alt text for avatar', () => {
    render(<Navigation />);

    // Avatar image should have proper alt text (fallback shows when no image)
    const avatar = screen.getByText('J'); // Avatar fallback shows first letter
    expect(avatar).toBeInTheDocument();
  });

  it('should hide decorative icons from screen readers', () => {
    render(<Navigation />);

    // Shield icon should be hidden from screen readers
    const shieldIcon = document.querySelector('[aria-hidden="true"]');
    expect(shieldIcon).toBeInTheDocument();
  });

  it('should support keyboard navigation', async () => {
    const user = userEvent.setup();
    render(<Navigation />);

    const menuButton = screen.getByRole('button', { name: /open user menu for john doe/i });

    // Should be able to focus and activate menu with keyboard
    await user.tab();
    expect(menuButton).toHaveFocus();

    // Open menu with Enter
    await user.keyboard('{Enter}');

    // Menu items should be accessible
    const profileItem = screen.getByText('Profile');
    expect(profileItem).toBeInTheDocument();
  });

  it('should announce user status with aria-live', () => {
    render(<Navigation />);

    // Welcome message should be announced to screen readers
    const welcomeMessage = screen.getByText(/welcome, john doe/i);
    expect(welcomeMessage).toHaveAttribute('aria-live', 'polite');
  });

  it('should have proper menu item structure', async () => {
    const user = userEvent.setup();
    render(<Navigation />);

    const menuButton = screen.getByRole('button', { name: /open user menu for john doe/i });
    await user.click(menuButton);

    // All menu items should be properly structured
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems).toHaveLength(3); // Profile, Settings, Log out

    // Each menu item should have text content
    menuItems.forEach(item => {
      expect(item).toHaveTextContent(/.+/);
    });
  });
});
