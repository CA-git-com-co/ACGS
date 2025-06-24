import type { Meta, StoryObj } from '@storybook/react';
import ComplianceChecker from './ComplianceChecker';
import { ActivePolicy, ComplianceResult } from '../types/governance';

/**
 * ComplianceChecker Component for ACGS-PGP Framework
 *
 * This component provides real-time compliance validation against governance policies
 * using the PGC (Prompt Governance Compiler) service. It demonstrates the core
 * constitutional governance workflow of the ACGS system.
 */

// Mock data for stories
const mockActivePolicies: ActivePolicy[] = [
  {
    id: 'POL-001',
    name: 'No Extrajudicial State Mutation',
    rules: [
      {
        id: 'R1',
        condition: 'action.type === "state_change" && !action.hasApproval',
        action: 'DENY'
      }
    ]
  },
  {
    id: 'POL-002',
    name: 'Treasury Protection Policy',
    rules: [
      {
        id: 'R1',
        condition: 'action.involvesFunds && action.amount > authorizedLimit',
        action: 'REQUIRE_GOVERNANCE_APPROVAL'
      }
    ]
  },
  {
    id: 'POL-003',
    name: 'Democratic Governance Requirement',
    rules: [
      {
        id: 'R1',
        condition: 'action.requiresGovernance && !action.hasGovernanceApproval',
        action: 'DENY'
      }
    ]
  }
];

const meta: Meta<typeof ComplianceChecker> = {
  title: 'Components/Governance/ComplianceChecker',
  component: ComplianceChecker,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
The ComplianceChecker component is a core part of the ACGS constitutional governance system.
It allows users to validate proposed actions against active governance policies using the
PGC (Prompt Governance Compiler) service.

**Key Features:**
- Real-time compliance validation
- Integration with PGC service (port 8005)
- Support for multiple policy types
- Detailed violation reporting
- Loading states and error handling
- Service error boundaries

**ACGS Integration:**
- Connects to PGC service for compliance validation
- Uses constitutional principles from AC service
- Supports policy synthesis from GS service
- Integrates with authentication and authorization
        `
      }
    },
    backgrounds: {
      default: 'governance'
    }
  },
  tags: ['autodocs'],
  argTypes: {
    activePolicies: {
      description: 'Array of active policies to check against',
      control: 'object'
    },
    onComplianceCheck: {
      description: 'Callback function called when compliance check completes',
      action: 'compliance-checked'
    },
    className: {
      description: 'Additional CSS classes',
      control: 'text'
    }
  }
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default ComplianceChecker with mock policies
 */
export const Default: Story = {
  args: {
    activePolicies: mockActivePolicies,
    onComplianceCheck: (result: ComplianceResult) => {
      console.log('Compliance check result:', result);
    }
  }
};

/**
 * ComplianceChecker without policies (will use internal mock data)
 */
export const WithoutPolicies: Story = {
  args: {
    onComplianceCheck: (result: ComplianceResult) => {
      console.log('Compliance check result:', result);
    }
  }
};

/**
 * ComplianceChecker with single policy
 */
export const SinglePolicy: Story = {
  args: {
    activePolicies: [mockActivePolicies[0]],
    onComplianceCheck: (result: ComplianceResult) => {
      console.log('Compliance check result:', result);
    }
  }
};

/**
 * ComplianceChecker with custom styling
 */
export const CustomStyling: Story = {
  args: {
    activePolicies: mockActivePolicies,
    className: 'border-2 border-blue-200 shadow-xl',
    onComplianceCheck: (result: ComplianceResult) => {
      console.log('Compliance check result:', result);
    }
  }
};

/**
 * Interactive demo showing different compliance scenarios
 */
export const InteractiveDemo: Story = {
  render: () => {
    const handleComplianceCheck = (result: ComplianceResult) => {
      alert(
        `Compliance Result: ${result.compliant ? 'COMPLIANT' : 'VIOLATION'}\nConfidence: ${result.confidenceScore}%${result.violationReasons ? '\nViolations: ' + result.violationReasons.join(', ') : ''}`
      );
    };

    return (
      <div className="space-y-6 max-w-4xl">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">🏛️ ACGS Constitutional Governance Demo</h3>
          <p className="text-blue-700 text-sm">
            This demo shows the PGC (Prompt Governance Compiler) in action. Try different actions to see how they are
            validated against constitutional principles and governance policies.
          </p>
        </div>

        <ComplianceChecker activePolicies={mockActivePolicies} onComplianceCheck={handleComplianceCheck} />

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-2">Example Actions to Test:</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• "Transfer 1000 tokens to treasury" (should be compliant)</li>
            <li>• "Transfer 10000 tokens without approval" (should violate treasury policy)</li>
            <li>• "Change system parameters without governance" (should violate governance policy)</li>
            <li>• "Update user profile" (should be compliant)</li>
            <li>• "Execute emergency protocol" (should require governance approval)</li>
          </ul>
        </div>
      </div>
    );
  }
};

/**
 * ComplianceChecker in different container sizes
 */
export const ResponsiveDemo: Story = {
  render: () => (
    <div className="space-y-8">
      <div className="w-96">
        <h3 className="text-lg font-semibold mb-4">Mobile Size (384px)</h3>
        <ComplianceChecker
          activePolicies={mockActivePolicies.slice(0, 1)}
          onComplianceCheck={result => console.log('Mobile result:', result)}
        />
      </div>

      <div className="w-full max-w-2xl">
        <h3 className="text-lg font-semibold mb-4">Tablet Size (768px)</h3>
        <ComplianceChecker
          activePolicies={mockActivePolicies.slice(0, 2)}
          onComplianceCheck={result => console.log('Tablet result:', result)}
        />
      </div>

      <div className="w-full max-w-4xl">
        <h3 className="text-lg font-semibold mb-4">Desktop Size (1024px+)</h3>
        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={result => console.log('Desktop result:', result)}
        />
      </div>
    </div>
  )
};

/**
 * ComplianceChecker with error simulation
 */
export const ErrorHandling: Story = {
  render: () => {
    // This would normally trigger service errors for demonstration
    return (
      <div className="space-y-4">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Error Handling Demo</h3>
          <p className="text-yellow-700 text-sm">
            This component includes comprehensive error boundaries and loading states. In a real environment, service
            errors would be caught and displayed gracefully.
          </p>
        </div>

        <ComplianceChecker
          activePolicies={mockActivePolicies}
          onComplianceCheck={result => console.log('Error demo result:', result)}
        />
      </div>
    );
  }
};
