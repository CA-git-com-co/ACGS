import { render, screen } from '@testing-library/react';
import { Button } from './button';

describe('Button', () => {
  it('renders button with default variant', () => {
    render(<Button>Test Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Test Button');
  });

  it('renders button with constitutional variant', () => {
    render(<Button constitutional>Constitutional Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-constitutional-600');
  });

  it('renders button with loading state', () => {
    render(<Button loading>Loading Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button.querySelector('svg')).toBeInTheDocument();
  });

  it('renders button with icon', () => {
    const icon = <span data-testid="icon">🎯</span>;
    render(<Button icon={icon}>Button with Icon</Button>);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });
});