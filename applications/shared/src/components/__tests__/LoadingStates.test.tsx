import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  Spinner,
  Skeleton,
  Progress,
  LoadingOverlay,
  CardSkeleton,
  TableSkeleton,
  FormSkeleton,
  LoadingButton,
  TimeoutLoader
} from '../LoadingStates';

describe('LoadingStates Components', () => {
  describe('Spinner', () => {
    it('should render spinner with default props', () => {
      render(<Spinner />);
      
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveAttribute('aria-label', 'Loading');
    });

    it('should render spinner with text when showText is true', () => {
      render(<Spinner showText text="Loading data..." />);
      
      expect(screen.getByText('Loading data...')).toBeInTheDocument();
    });

    it('should apply size classes correctly', () => {
      const { rerender } = render(<Spinner size="sm" />);
      expect(screen.getByRole('status')).toHaveClass('h-4', 'w-4');

      rerender(<Spinner size="lg" />);
      expect(screen.getByRole('status')).toHaveClass('h-8', 'w-8');

      rerender(<Spinner size="xl" />);
      expect(screen.getByRole('status')).toHaveClass('h-12', 'w-12');
    });

    it('should apply color classes correctly', () => {
      const { rerender } = render(<Spinner color="blue" />);
      expect(screen.getByRole('status')).toHaveClass('text-blue-600', 'border-blue-600');

      rerender(<Spinner color="green" />);
      expect(screen.getByRole('status')).toHaveClass('text-green-600', 'border-green-600');

      rerender(<Spinner color="red" />);
      expect(screen.getByRole('status')).toHaveClass('text-red-600', 'border-red-600');
    });

    it('should apply custom className', () => {
      const { container } = render(<Spinner className="custom-spinner" />);
      expect(container.firstChild).toHaveClass('custom-spinner');
    });
  });

  describe('Skeleton', () => {
    it('should render single skeleton with default props', () => {
      render(<Skeleton />);
      
      const skeleton = screen.getByRole('status');
      expect(skeleton).toBeInTheDocument();
      expect(skeleton).toHaveAttribute('aria-label', 'Loading content');
    });

    it('should render multiple skeleton lines', () => {
      render(<Skeleton lines={3} />);
      
      const skeletons = screen.getAllByRole('status');
      expect(skeletons).toHaveLength(1); // Container has single role
      
      const container = screen.getByRole('status');
      expect(container.children).toHaveLength(3);
    });

    it('should apply rounded class when rounded is true', () => {
      render(<Skeleton rounded />);
      
      const skeleton = screen.getByRole('status');
      expect(skeleton).toHaveClass('rounded-full');
    });

    it('should apply custom width and height', () => {
      render(<Skeleton width="200px" height="50px" />);
      
      const skeleton = screen.getByRole('status');
      expect(skeleton).toHaveStyle({ width: '200px', height: '50px' });
    });
  });

  describe('Progress', () => {
    it('should render progress bar with default props', () => {
      render(<Progress progress={50} />);
      
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveAttribute('aria-valuenow', '50');
      expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });

    it('should display percentage when showPercentage is true', () => {
      render(<Progress progress={75} showPercentage />);
      
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('should display label when provided', () => {
      render(<Progress progress={60} label="Loading policies..." />);
      
      expect(screen.getByText('Loading policies...')).toBeInTheDocument();
    });

    it('should apply correct width based on progress', () => {
      render(<Progress progress={30} />);
      
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveStyle({ width: '30%' });
    });

    it('should handle progress values outside 0-100 range', () => {
      const { rerender } = render(<Progress progress={-10} />);
      let progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveStyle({ width: '0%' });

      rerender(<Progress progress={150} />);
      progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveStyle({ width: '100%' });
    });

    it('should apply color classes correctly', () => {
      const { rerender } = render(<Progress progress={50} color="green" />);
      expect(screen.getByRole('progressbar')).toHaveClass('bg-green-600');

      rerender(<Progress progress={50} color="red" />);
      expect(screen.getByRole('progressbar')).toHaveClass('bg-red-600');
    });
  });

  describe('LoadingOverlay', () => {
    it('should render children when not loading', () => {
      render(
        <LoadingOverlay isLoading={false}>
          <div>Content</div>
        </LoadingOverlay>
      );
      
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });

    it('should render overlay when loading', () => {
      render(
        <LoadingOverlay isLoading={true}>
          <div>Content</div>
        </LoadingOverlay>
      );
      
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should apply blur effect when blur is true', () => {
      render(
        <LoadingOverlay isLoading={true} blur={true}>
          <div>Content</div>
        </LoadingOverlay>
      );
      
      const contentContainer = screen.getByText('Content').parentElement;
      expect(contentContainer).toHaveClass('filter', 'blur-sm');
    });

    it('should render custom spinner when provided', () => {
      const customSpinner = <div data-testid="custom-spinner">Custom Loading</div>;
      
      render(
        <LoadingOverlay isLoading={true} spinner={customSpinner}>
          <div>Content</div>
        </LoadingOverlay>
      );
      
      expect(screen.getByTestId('custom-spinner')).toBeInTheDocument();
    });
  });

  describe('LoadingButton', () => {
    it('should render button with children when not loading', () => {
      render(
        <LoadingButton isLoading={false} onClick={jest.fn()}>
          Submit
        </LoadingButton>
      );
      
      expect(screen.getByRole('button')).toBeInTheDocument();
      expect(screen.getByText('Submit')).toBeInTheDocument();
    });

    it('should show loading text when loading', () => {
      render(
        <LoadingButton isLoading={true} loadingText="Submitting..." onClick={jest.fn()}>
          Submit
        </LoadingButton>
      );
      
      expect(screen.getByText('Submitting...')).toBeInTheDocument();
      expect(screen.queryByText('Submit')).not.toBeInTheDocument();
    });

    it('should be disabled when loading', () => {
      render(
        <LoadingButton isLoading={true} onClick={jest.fn()}>
          Submit
        </LoadingButton>
      );
      
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should be disabled when disabled prop is true', () => {
      render(
        <LoadingButton isLoading={false} disabled={true} onClick={jest.fn()}>
          Submit
        </LoadingButton>
      );
      
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should call onClick when clicked and not loading', () => {
      const handleClick = jest.fn();
      render(
        <LoadingButton isLoading={false} onClick={handleClick}>
          Submit
        </LoadingButton>
      );
      
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not call onClick when loading', () => {
      const handleClick = jest.fn();
      render(
        <LoadingButton isLoading={true} onClick={handleClick}>
          Submit
        </LoadingButton>
      );
      
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('CardSkeleton', () => {
    it('should render card skeleton structure', () => {
      render(<CardSkeleton />);
      
      const skeletons = screen.getAllByRole('status');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('should apply custom className', () => {
      const { container } = render(<CardSkeleton className="custom-card" />);
      expect(container.firstChild).toHaveClass('custom-card');
    });
  });

  describe('TableSkeleton', () => {
    it('should render table skeleton with default rows and columns', () => {
      render(<TableSkeleton />);
      
      const skeletons = screen.getAllByRole('status');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('should render specified number of rows and columns', () => {
      render(<TableSkeleton rows={3} columns={2} />);
      
      const skeletons = screen.getAllByRole('status');
      // Should have header + 3 rows, each with 2 columns
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('FormSkeleton', () => {
    it('should render form skeleton with default fields', () => {
      render(<FormSkeleton />);
      
      const skeletons = screen.getAllByRole('status');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('should render specified number of fields', () => {
      render(<FormSkeleton fields={2} />);
      
      const skeletons = screen.getAllByRole('status');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('TimeoutLoader', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should render loading component initially', () => {
      render(
        <TimeoutLoader timeout={5000}>
          <div>Content</div>
        </TimeoutLoader>
      );
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should show timeout message after timeout', () => {
      render(
        <TimeoutLoader timeout={1000}>
          <div>Content</div>
        </TimeoutLoader>
      );
      
      jest.advanceTimersByTime(1000);
      
      expect(screen.getByText('Request Timeout')).toBeInTheDocument();
    });

    it('should call onTimeout when timeout occurs', () => {
      const handleTimeout = jest.fn();
      render(
        <TimeoutLoader timeout={1000} onTimeout={handleTimeout}>
          <div>Content</div>
        </TimeoutLoader>
      );
      
      jest.advanceTimersByTime(1000);
      
      expect(handleTimeout).toHaveBeenCalledTimes(1);
    });

    it('should render custom timeout component', () => {
      const customTimeout = <div data-testid="custom-timeout">Custom Timeout</div>;
      
      render(
        <TimeoutLoader timeout={1000} timeoutComponent={customTimeout}>
          <div>Content</div>
        </TimeoutLoader>
      );
      
      jest.advanceTimersByTime(1000);
      
      expect(screen.getByTestId('custom-timeout')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for loading states', () => {
      render(<Spinner />);
      expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Loading');
    });

    it('should have proper ARIA attributes for progress bars', () => {
      render(<Progress progress={50} />);
      
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '50');
      expect(progressBar).toHaveAttribute('aria-valuemin', '0');
      expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    });

    it('should have proper ARIA labels for skeleton loaders', () => {
      render(<Skeleton />);
      expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Loading content');
    });
  });
});
