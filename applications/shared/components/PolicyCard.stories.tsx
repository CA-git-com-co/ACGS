import type { Meta, StoryObj } from '@storybook/react';
import PolicyCard from './PolicyCard';
import { Policy } from '../types/governance';

/**
 * PolicyCard Component for ACGS-PGP Framework
 *
 * This component displays governance policies with their validation scores,
 * complexity metrics, and action buttons. It integrates with the GS (Governance
 * Synthesis) service for policy management and lifecycle operations.
 */

// Mock policy data for stories
const mockPolicy: Policy = {
  id: 'POL-001',
  name: 'Treasury Protection Policy',
  description:
    'Comprehensive policy to protect treasury funds from unauthorized access and ensure proper governance approval for financial transactions exceeding predefined limits.',
  rules: [
    {
      id: 'R1',
      condition: 'transaction.amount > treasury.authorizedLimit',
      action: 'REQUIRE_GOVERNANCE_APPROVAL'
    },
    {
      id: 'R2',
      condition: 'transaction.recipient.isExternal && !transaction.hasMultiSigApproval',
      action: 'DENY'
    },
    {
      id: 'R3',
      condition: 'transaction.type === "emergency" && governance.emergencyProtocolActive',
      action: 'ALLOW_WITH_AUDIT'
    }
  ],
  validationScore: 95,
  complianceComplexity: 35,
  status: 'active',
  category: 'financial',
  createdAt: new Date('2024-01-15T10:30:00Z'),
  updatedAt: new Date('2024-01-20T14:45:00Z'),
  author: 'governance-system'
};

const draftPolicy: Policy = {
  ...mockPolicy,
  id: 'POL-002',
  name: 'Democratic Voting Requirements',
  description:
    'Policy ensuring all constitutional changes require democratic voting with proper quorum and transparency.',
  status: 'draft',
  validationScore: 78,
  complianceComplexity: 60,
  category: 'governance'
};

const archivedPolicy: Policy = {
  ...mockPolicy,
  id: 'POL-003',
  name: 'Legacy Access Control',
  description: 'Deprecated access control policy replaced by modern constitutional governance framework.',
  status: 'archived',
  validationScore: 45,
  complianceComplexity: 85,
  category: 'security'
};

const meta: Meta<typeof PolicyCard> = {
  title: 'Components/Policy/PolicyCard',
  component: PolicyCard,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
The PolicyCard component displays governance policies with comprehensive metadata,
validation scores, and management actions. It's a key component in the ACGS
policy management interface.

**Key Features:**
- Policy status indicators (active, draft, archived)
- Validation score and complexity metrics
- Rule display with syntax highlighting
- Action buttons for policy lifecycle management
- Loading states for async operations
- Responsive design for different screen sizes

**ACGS Integration:**
- Connects to GS service for policy operations
- Displays policies synthesized from constitutional principles
- Supports policy activation, deactivation, and editing
- Integrates with compliance validation system
        `
      }
    },
    backgrounds: {
      default: 'governance'
    }
  },
  tags: ['autodocs'],
  argTypes: {
    policy: {
      description: 'Policy object to display',
      control: 'object'
    },
    onActivate: {
      description: 'Callback when activate button is clicked',
      action: 'policy-activated'
    },
    onDeactivate: {
      description: 'Callback when deactivate button is clicked',
      action: 'policy-deactivated'
    },
    onEdit: {
      description: 'Callback when edit button is clicked',
      action: 'policy-edited'
    },
    isLoading: {
      description: 'Loading state for async operations',
      control: 'boolean'
    }
  }
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Active policy with high validation score
 */
export const ActivePolicy: Story = {
  args: {
    policy: mockPolicy,
    isLoading: false,
    onActivate: (id: string) => console.log('Activate policy:', id),
    onDeactivate: (id: string) => console.log('Deactivate policy:', id),
    onEdit: (policy: Policy) => console.log('Edit policy:', policy)
  }
};

/**
 * Draft policy ready for activation
 */
export const DraftPolicy: Story = {
  args: {
    policy: draftPolicy,
    isLoading: false,
    onActivate: (id: string) => console.log('Activate policy:', id),
    onEdit: (policy: Policy) => console.log('Edit policy:', policy)
  }
};

/**
 * Archived policy (read-only)
 */
export const ArchivedPolicy: Story = {
  args: {
    policy: archivedPolicy,
    isLoading: false,
    onEdit: (policy: Policy) => console.log('Edit policy:', policy)
  }
};

/**
 * Policy card in loading state
 */
export const LoadingState: Story = {
  args: {
    policy: mockPolicy,
    isLoading: true,
    onActivate: (id: string) => console.log('Activate policy:', id),
    onDeactivate: (id: string) => console.log('Deactivate policy:', id),
    onEdit: (policy: Policy) => console.log('Edit policy:', policy)
  }
};

/**
 * Policy with low validation score
 */
export const LowValidationScore: Story = {
  args: {
    policy: {
      ...mockPolicy,
      validationScore: 45,
      complianceComplexity: 85,
      status: 'draft' as const
    },
    isLoading: false,
    onActivate: (id: string) => console.log('Activate policy:', id),
    onEdit: (policy: Policy) => console.log('Edit policy:', policy)
  }
};

/**
 * Policy with many rules
 */
export const ComplexPolicy: Story = {
  args: {
    policy: {
      ...mockPolicy,
      name: 'Comprehensive Governance Framework',
      description:
        'Multi-faceted policy covering various aspects of constitutional governance, democratic processes, and system integrity.',
      rules: [
        { id: 'R1', condition: 'proposal.type === "constitutional"', action: 'REQUIRE_SUPERMAJORITY' },
        { id: 'R2', condition: 'vote.quorum < governance.minimumQuorum', action: 'DEFER_VOTE' },
        { id: 'R3', condition: 'amendment.impact === "high"', action: 'REQUIRE_REVIEW_PERIOD' },
        { id: 'R4', condition: 'user.role !== "verified"', action: 'RESTRICT_VOTING' },
        { id: 'R5', condition: 'system.emergencyMode === true', action: 'ENABLE_EMERGENCY_PROTOCOLS' },
        { id: 'R6', condition: 'transaction.amount > limits.daily', action: 'REQUIRE_MULTI_SIG' }
      ],
      complianceComplexity: 75
    },
    isLoading: false,
    onDeactivate: (id: string) => console.log('Deactivate policy:', id),
    onEdit: (policy: Policy) => console.log('Edit policy:', policy)
  }
};

/**
 * Grid of policy cards showing different states
 */
export const PolicyGrid: Story = {
  render: () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 max-w-7xl">
      <PolicyCard
        policy={mockPolicy}
        onDeactivate={id => console.log('Deactivate:', id)}
        onEdit={policy => console.log('Edit:', policy)}
      />
      <PolicyCard
        policy={draftPolicy}
        onActivate={id => console.log('Activate:', id)}
        onEdit={policy => console.log('Edit:', policy)}
      />
      <PolicyCard policy={archivedPolicy} onEdit={policy => console.log('Edit:', policy)} />
      <PolicyCard
        policy={{
          ...mockPolicy,
          id: 'POL-004',
          name: 'Emergency Response Protocol',
          status: 'active' as const,
          validationScore: 88,
          complianceComplexity: 45,
          category: 'emergency'
        }}
        isLoading={true}
      />
    </div>
  )
};

/**
 * Interactive demo with all actions
 */
export const InteractiveDemo: Story = {
  render: () => {
    const handleActivate = (id: string) => {
      alert(`Activating policy: ${id}\n\nThis would send a request to the GS service to activate the policy.`);
    };

    const handleDeactivate = (id: string) => {
      alert(`Deactivating policy: ${id}\n\nThis would send a request to the GS service to deactivate the policy.`);
    };

    const handleEdit = (policy: Policy) => {
      alert(`Editing policy: ${policy.name}\n\nThis would open the policy editor with the current policy data.`);
    };

    return (
      <div className="space-y-6 max-w-4xl">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">📋 Policy Management Demo</h3>
          <p className="text-blue-700 text-sm">
            This demo shows policy cards with different states and actions. Click the buttons to see how policy
            lifecycle management works in the ACGS system.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PolicyCard policy={draftPolicy} onActivate={handleActivate} onEdit={handleEdit} />
          <PolicyCard policy={mockPolicy} onDeactivate={handleDeactivate} onEdit={handleEdit} />
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-2">Policy Lifecycle:</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>
              • <strong>Draft:</strong> Policy is being developed and can be activated
            </li>
            <li>
              • <strong>Active:</strong> Policy is enforced and can be deactivated
            </li>
            <li>
              • <strong>Archived:</strong> Policy is no longer active but kept for reference
            </li>
          </ul>
        </div>
      </div>
    );
  }
};
