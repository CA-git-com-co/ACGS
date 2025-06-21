// Governance Domain Components (AC Service)
//
// Components related to constitutional principles, amendments,
// and governance workflows managed by the AC service.

import { withACProtection, withGovernanceProtection } from '../hoc/composite';

// Re-export governance-related components with domain-specific protection
export { default as PrincipleCard } from '../PrincipleCard';

// Protected versions of governance components
export const ProtectedPrincipleCard = withGovernanceProtection(require('../PrincipleCard').default);

// Container components for governance features
export { default as PrincipleList } from '../containers/PrincipleList';
export { default as PrincipleForm } from '../containers/PrincipleForm';
export { default as AmendmentWorkflow } from '../containers/AmendmentWorkflow';

// Presentation components for governance
export { default as PrincipleDisplay } from '../presentation/PrincipleDisplay';
export { default as AmendmentCard } from '../presentation/AmendmentCard';
export { default as VotingInterface } from '../presentation/VotingInterface';

// Governance-specific hooks
export { useGovernance } from '../../hooks/useGovernance';
export { usePrinciples } from '../../hooks/usePrinciples';
export { useAmendments } from '../../hooks/useAmendments';

// Governance types
export type { Principle, Amendment, AmendmentVote } from '../../types/governance';
