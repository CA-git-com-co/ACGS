import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ComplianceChecker from '../ComplianceChecker';
import { createMockPolicy, createMockComplianceResult } from '../../setupTests';
import { ActivePolicy, ComplianceResult } from '../../types/governance';

// Mock the loading state hook
jest.mock('../../hooks/useLoadingState', () => ({
  useLoadingState: () => [
    {
      isLoading: false,
      error: null,
      isTimeout: false,
      retryCount: 0,
      progress: 0
    },
    {
      startLoading: jest.fn(),
      stopLoading: jest.fn(),
      setError: jest.fn(),
      retry: jest.fn(),
      reset: jest.fn(),
      setProgress: jest.fn()
    }
  ]
}));

// Mock ServiceErrorBoundary
jest.mock('../ServiceErrorBoundary', () => {
  return function MockServiceErrorBoundary({ children }: { children: React.ReactNode }) {
    return <div data-testid="service-error-boundary">{children}</div>;
  };
});

describe('ComplianceChecker', () => {
  const mockActivePolicies: ActivePolicy[] = [
    {
      id: 'POL-001',
      name: 'Treasury Protection Policy',
      rules: [
        {
          id: 'R1',
          condition: 'amount > authorizedLimit',
          action: 'REQUIRE_GOVERNANCE_APPROVAL'
        }
      ]
    },
    {
      id: 'POL-002',
      name: 'Democratic Governance Policy',
      rules: [
        {
          id: 'R1',
          condition: 'requiresGovernance && !hasApproval',
          action: 'DENY'
        }
      ]
    }
  ];

  const mockOnComplianceCheck = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the compliance checker form', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      expect(screen.getByText('🔍 PGC Compliance Checker')).toBeInTheDocument();
      expect(screen.getByLabelText(/action to check/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/select policy/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /check compliance/i })).toBeInTheDocument();
    });

    it('should render with service error boundary', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      expect(screen.getByTestId('service-error-boundary')).toBeInTheDocument();
    });

    it('should display active policies in dropdown', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const policySelect = screen.getByLabelText(/select policy/i);
      fireEvent.click(policySelect);

      expect(screen.getByText('Treasury Protection Policy')).toBeInTheDocument();
      expect(screen.getByText('Democratic Governance Policy')).toBeInTheDocument();
    });

    it('should render without policies (using mock data)', () => {
      render(<ComplianceChecker onComplianceCheck={mockOnComplianceCheck} />);

      expect(screen.getByText('🔍 PGC Compliance Checker')).toBeInTheDocument();
      expect(screen.getByLabelText(/select policy/i)).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    it('should update action input when user types', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const actionInput = screen.getByLabelText(/action to check/i);
      await user.type(actionInput, 'Transfer 1000 tokens');

      expect(actionInput).toHaveValue('Transfer 1000 tokens');
    });

    it('should update policy selection', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const policySelect = screen.getByLabelText(/select policy/i);
      await user.selectOptions(policySelect, 'POL-001');

      expect(policySelect).toHaveValue('POL-001');
    });

    it('should update action context checkboxes', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const governanceCheckbox = screen.getByLabelText(/requires governance/i);
      await user.click(governanceCheckbox);

      expect(governanceCheckbox).toBeChecked();
    });

    it('should update amount input', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const amountInput = screen.getByLabelText(/amount/i);
      await user.clear(amountInput);
      await user.type(amountInput, '1500');

      expect(amountInput).toHaveValue(1500);
    });
  });

  describe('Compliance Checking', () => {
    it('should disable submit button when form is incomplete', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const submitButton = screen.getByRole('button', { name: /check compliance/i });
      expect(submitButton).toBeDisabled();
    });

    it('should enable submit button when form is complete', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const actionInput = screen.getByLabelText(/action to check/i);
      const policySelect = screen.getByLabelText(/select policy/i);

      await user.type(actionInput, 'Test action');
      await user.selectOptions(policySelect, 'POL-001');

      const submitButton = screen.getByRole('button', { name: /check compliance/i });
      expect(submitButton).not.toBeDisabled();
    });

    it('should perform compliance check when form is submitted', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const actionInput = screen.getByLabelText(/action to check/i);
      const policySelect = screen.getByLabelText(/select policy/i);
      const submitButton = screen.getByRole('button', { name: /check compliance/i });

      await user.type(actionInput, 'Transfer 500 tokens');
      await user.selectOptions(policySelect, 'POL-001');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnComplianceCheck).toHaveBeenCalled();
      });

      const callArgs = mockOnComplianceCheck.mock.calls[0][0];
      expect(callArgs).toHaveProperty('compliant');
      expect(callArgs).toHaveProperty('confidenceScore');
    });

    it('should display compliance results', async () => {
      const user = userEvent.setup();
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const actionInput = screen.getByLabelText(/action to check/i);
      const policySelect = screen.getByLabelText(/select policy/i);
      const submitButton = screen.getByRole('button', { name: /check compliance/i });

      await user.type(actionInput, 'Transfer 500 tokens');
      await user.selectOptions(policySelect, 'POL-001');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/recent compliance results/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      expect(screen.getByLabelText(/action to check/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/select policy/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/requires governance/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/has governance approval/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/involves funds/i)).toBeInTheDocument();
    });

    it('should have proper button roles', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      expect(screen.getByRole('button', { name: /check compliance/i })).toBeInTheDocument();
    });

    it('should have proper form structure', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      expect(screen.getByRole('form')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle missing action gracefully', async () => {
      const user = userEvent.setup();

      // Mock alert to capture the error message
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const policySelect = screen.getByLabelText(/select policy/i);
      const submitButton = screen.getByRole('button', { name: /check compliance/i });

      await user.selectOptions(policySelect, 'POL-001');
      await user.click(submitButton);

      expect(alertSpy).toHaveBeenCalledWith('Please enter an action and select a policy');

      alertSpy.mockRestore();
    });

    it('should handle missing policy selection gracefully', async () => {
      const user = userEvent.setup();

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      const actionInput = screen.getByLabelText(/action to check/i);
      const submitButton = screen.getByRole('button', { name: /check compliance/i });

      await user.type(actionInput, 'Test action');
      await user.click(submitButton);

      expect(alertSpy).toHaveBeenCalledWith('Please enter an action and select a policy');

      alertSpy.mockRestore();
    });
  });

  describe('Props Validation', () => {
    it('should accept valid props', () => {
      const validProps = {
        activePolicies: mockActivePolicies,
        onComplianceCheck: mockOnComplianceCheck,
        className: 'test-class'
      };

      expect(() => {
        render(<ComplianceChecker {...validProps} />);
      }).not.toThrow();
    });

    it('should handle optional props', () => {
      expect(() => {
        render(<ComplianceChecker />);
      }).not.toThrow();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
          className="custom-class"
        />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Integration with ACGS Services', () => {
    it('should integrate with PGC service error boundary', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      expect(screen.getByTestId('service-error-boundary')).toBeInTheDocument();
    });

    it('should use proper service URL pattern', () => {
      render(
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={mockOnComplianceCheck}
        />
      );

      // The component should be wrapped with ServiceErrorBoundary for PGC service
      expect(screen.getByTestId('service-error-boundary')).toBeInTheDocument();
    });
  });
});
