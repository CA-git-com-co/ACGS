import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthContext } from '../../contexts/AuthContext';
import ACService from '../../services/ACService';
import GSService from '../../services/GSService';
import ComplianceChecker from '../../components/ComplianceChecker';
import {
  createMockUser,
  createMockPrinciple,
  createMockPolicy,
  mockServiceResponses
} from '../../setupTests';

// Mock the services
jest.mock('../../services/ACService');
jest.mock('../../services/GSService');

const MockedACService = ACService as jest.Mocked<typeof ACService>;
const MockedGSService = GSService as jest.Mocked<typeof GSService>;

// Mock AuthContext Provider
const MockAuthProvider: React.FC<{ children: React.ReactNode; user?: any }> = ({
  children,
  user = createMockUser()
}) => {
  const authValue = {
    currentUser: user,
    isAuthenticated: !!user,
    isLoading: false,
    login: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn()
  };

  return <AuthContext.Provider value={authValue}>{children}</AuthContext.Provider>;
};

describe('Service Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Setup default mock responses
    MockedACService.getPrinciples.mockResolvedValue({
      principles: [createMockPrinciple()]
    });

    MockedACService.createPrinciple.mockImplementation(data =>
      Promise.resolve(createMockPrinciple(data))
    );

    MockedGSService.synthesizePolicies.mockResolvedValue({
      policies: [createMockPolicy()],
      validationScore: 90,
      complianceComplexity: 25
    });
  });

  describe('Authentication Service Integration', () => {
    it('should handle authenticated user state', () => {
      const mockUser = createMockUser({ role: 'admin' });

      render(
        <MockAuthProvider user={mockUser}>
          <div data-testid="auth-content">Authenticated Content</div>
        </MockAuthProvider>
      );

      expect(screen.getByTestId('auth-content')).toBeInTheDocument();
    });

    it('should handle unauthenticated state', () => {
      render(
        <MockAuthProvider user={null}>
          <div data-testid="unauth-content">Unauthenticated Content</div>
        </MockAuthProvider>
      );

      expect(screen.getByTestId('unauth-content')).toBeInTheDocument();
    });

    it('should provide authentication context to components', () => {
      const TestComponent = () => {
        const { currentUser, isAuthenticated } = React.useContext(AuthContext);
        return (
          <div>
            <span data-testid="auth-status">
              {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
            </span>
            <span data-testid="user-role">{currentUser?.role || 'No Role'}</span>
          </div>
        );
      };

      const mockUser = createMockUser({ role: 'moderator' });

      render(
        <MockAuthProvider user={mockUser}>
          <TestComponent />
        </MockAuthProvider>
      );

      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-role')).toHaveTextContent('moderator');
    });
  });

  describe('AC Service Integration', () => {
    it('should fetch principles successfully', async () => {
      const mockPrinciples = [
        createMockPrinciple({ id: 'PRIN-001', title: 'Test Principle 1' }),
        createMockPrinciple({ id: 'PRIN-002', title: 'Test Principle 2' })
      ];

      MockedACService.getPrinciples.mockResolvedValue({
        principles: mockPrinciples
      });

      const TestComponent = () => {
        const [principles, setPrinciples] = React.useState([]);
        const [loading, setLoading] = React.useState(false);

        const fetchPrinciples = async () => {
          setLoading(true);
          try {
            const response = await ACService.getPrinciples();
            setPrinciples(response.principles);
          } finally {
            setLoading(false);
          }
        };

        React.useEffect(() => {
          fetchPrinciples();
        }, []);

        return (
          <div>
            {loading ? (
              <div data-testid="loading">Loading...</div>
            ) : (
              <div data-testid="principles-list">
                {principles.map((principle: any) => (
                  <div key={principle.id} data-testid={`principle-${principle.id}`}>
                    {principle.title}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      };

      render(
        <MockAuthProvider>
          <TestComponent />
        </MockAuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('principles-list')).toBeInTheDocument();
      });

      expect(screen.getByTestId('principle-PRIN-001')).toHaveTextContent('Test Principle 1');
      expect(screen.getByTestId('principle-PRIN-002')).toHaveTextContent('Test Principle 2');
      expect(MockedACService.getPrinciples).toHaveBeenCalledTimes(1);
    });

    it('should create principle successfully', async () => {
      const newPrincipleData = {
        title: 'New Principle',
        content: 'New principle content',
        category: 'governance',
        priority: 8
      };

      const createdPrinciple = createMockPrinciple({
        id: 'PRIN-NEW',
        ...newPrincipleData
      });

      MockedACService.createPrinciple.mockResolvedValue(createdPrinciple);

      const TestComponent = () => {
        const [result, setResult] = React.useState(null);

        const handleCreate = async () => {
          const created = await ACService.createPrinciple(newPrincipleData);
          setResult(created);
        };

        return (
          <div>
            <button onClick={handleCreate} data-testid="create-button">
              Create Principle
            </button>
            {result && <div data-testid="created-principle">{result.title}</div>}
          </div>
        );
      };

      render(
        <MockAuthProvider>
          <TestComponent />
        </MockAuthProvider>
      );

      fireEvent.click(screen.getByTestId('create-button'));

      await waitFor(() => {
        expect(screen.getByTestId('created-principle')).toHaveTextContent('New Principle');
      });

      expect(MockedACService.createPrinciple).toHaveBeenCalledWith(newPrincipleData);
    });

    it('should handle AC service errors gracefully', async () => {
      MockedACService.getPrinciples.mockRejectedValue(new Error('AC Service unavailable'));

      const TestComponent = () => {
        const [error, setError] = React.useState('');

        const fetchPrinciples = async () => {
          try {
            await ACService.getPrinciples();
          } catch (err: any) {
            setError(err.message);
          }
        };

        React.useEffect(() => {
          fetchPrinciples();
        }, []);

        return <div>{error && <div data-testid="error-message">{error}</div>}</div>;
      };

      render(
        <MockAuthProvider>
          <TestComponent />
        </MockAuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toHaveTextContent('AC Service unavailable');
      });
    });
  });

  describe('GS Service Integration', () => {
    it('should synthesize policies successfully', async () => {
      const synthesisRequest = {
        principles: [{ id: 'PRIN-001' }, { id: 'PRIN-002' }]
      };

      const synthesisResult = {
        policies: [createMockPolicy({ name: 'Synthesized Policy' })],
        validationScore: 95,
        complianceComplexity: 20
      };

      MockedGSService.synthesizePolicies.mockResolvedValue(synthesisResult);

      const TestComponent = () => {
        const [result, setResult] = React.useState(null);

        const handleSynthesize = async () => {
          const synthesized = await GSService.synthesizePolicies(synthesisRequest);
          setResult(synthesized);
        };

        return (
          <div>
            <button onClick={handleSynthesize} data-testid="synthesize-button">
              Synthesize Policies
            </button>
            {result && (
              <div data-testid="synthesis-result">
                <div data-testid="validation-score">Score: {result.validationScore}</div>
                <div data-testid="policy-count">Policies: {result.policies.length}</div>
              </div>
            )}
          </div>
        );
      };

      render(
        <MockAuthProvider>
          <TestComponent />
        </MockAuthProvider>
      );

      fireEvent.click(screen.getByTestId('synthesize-button'));

      await waitFor(() => {
        expect(screen.getByTestId('synthesis-result')).toBeInTheDocument();
      });

      expect(screen.getByTestId('validation-score')).toHaveTextContent('Score: 95');
      expect(screen.getByTestId('policy-count')).toHaveTextContent('Policies: 1');
      expect(MockedGSService.synthesizePolicies).toHaveBeenCalledWith(synthesisRequest);
    });
  });

  describe('End-to-End Governance Workflow', () => {
    it('should complete principle creation to policy synthesis workflow', async () => {
      const user = userEvent.setup();

      // Mock the complete workflow
      const newPrinciple = createMockPrinciple({
        id: 'PRIN-NEW',
        title: 'Democratic Voting',
        content: 'All decisions require democratic voting'
      });

      MockedACService.createPrinciple.mockResolvedValue(newPrinciple);
      MockedGSService.synthesizePolicies.mockResolvedValue({
        policies: [createMockPolicy({ name: 'Democratic Voting Policy' })],
        validationScore: 92,
        complianceComplexity: 15
      });

      const WorkflowComponent = () => {
        const [principle, setPrinciple] = React.useState(null);
        const [policies, setPolicies] = React.useState([]);
        const [step, setStep] = React.useState(1);

        const createPrinciple = async () => {
          const created = await ACService.createPrinciple({
            title: 'Democratic Voting',
            content: 'All decisions require democratic voting',
            category: 'governance',
            priority: 9
          });
          setPrinciple(created);
          setStep(2);
        };

        const synthesizePolicies = async () => {
          if (principle) {
            const result = await GSService.synthesizePolicies({
              principles: [{ id: principle.id }]
            });
            setPolicies(result.policies);
            setStep(3);
          }
        };

        return (
          <div>
            <div data-testid="current-step">Step: {step}</div>

            {step === 1 && (
              <button onClick={createPrinciple} data-testid="create-principle">
                Create Principle
              </button>
            )}

            {step === 2 && principle && (
              <div>
                <div data-testid="created-principle">{principle.title}</div>
                <button onClick={synthesizePolicies} data-testid="synthesize-policies">
                  Synthesize Policies
                </button>
              </div>
            )}

            {step === 3 && (
              <div data-testid="workflow-complete">
                Workflow Complete: {policies.length} policies created
              </div>
            )}
          </div>
        );
      };

      render(
        <MockAuthProvider>
          <WorkflowComponent />
        </MockAuthProvider>
      );

      // Step 1: Create principle
      expect(screen.getByTestId('current-step')).toHaveTextContent('Step: 1');
      await user.click(screen.getByTestId('create-principle'));

      // Step 2: Principle created, synthesize policies
      await waitFor(() => {
        expect(screen.getByTestId('current-step')).toHaveTextContent('Step: 2');
      });
      expect(screen.getByTestId('created-principle')).toHaveTextContent('Democratic Voting');

      await user.click(screen.getByTestId('synthesize-policies'));

      // Step 3: Workflow complete
      await waitFor(() => {
        expect(screen.getByTestId('current-step')).toHaveTextContent('Step: 3');
      });
      expect(screen.getByTestId('workflow-complete')).toHaveTextContent(
        'Workflow Complete: 1 policies created'
      );

      // Verify service calls
      expect(MockedACService.createPrinciple).toHaveBeenCalledTimes(1);
      expect(MockedGSService.synthesizePolicies).toHaveBeenCalledTimes(1);
    });
  });

  describe('Component Service Integration', () => {
    it('should integrate ComplianceChecker with PGC service patterns', async () => {
      const user = userEvent.setup();
      const mockOnComplianceCheck = jest.fn();

      const activePolicies = [
        {
          id: 'POL-001',
          name: 'Test Policy',
          rules: [{ id: 'R1', condition: 'test', action: 'ALLOW' }]
        }
      ];

      render(
        <MockAuthProvider>
          <ComplianceChecker
            activePolicies={activePolicies}
            onComplianceCheck={mockOnComplianceCheck}
          />
        </MockAuthProvider>
      );

      // Fill out the form
      const actionInput = screen.getByLabelText(/action to check/i);
      const policySelect = screen.getByLabelText(/select policy/i);
      const submitButton = screen.getByRole('button', { name: /check compliance/i });

      await user.type(actionInput, 'Test governance action');
      await user.selectOptions(policySelect, 'POL-001');
      await user.click(submitButton);

      // Verify compliance check was called
      await waitFor(() => {
        expect(mockOnComplianceCheck).toHaveBeenCalled();
      });

      const complianceResult = mockOnComplianceCheck.mock.calls[0][0];
      expect(complianceResult).toHaveProperty('compliant');
      expect(complianceResult).toHaveProperty('confidenceScore');
    });
  });
});
