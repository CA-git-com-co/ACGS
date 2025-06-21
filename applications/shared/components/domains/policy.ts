// Policy Domain Components (GS Service)
//
// Components related to policy synthesis, management,
// and governance workflows managed by the GS service.

import { withGSProtection, withPolicyProtection } from '../hoc/composite';

// Re-export policy-related components
export { default as PolicyCard } from '../PolicyCard';
export { default as PolicyProposal } from '../PolicyProposal';

// Protected versions of policy components
export const ProtectedPolicyCard = withPolicyProtection(require('../PolicyCard').default);

export const ProtectedPolicyProposal = withPolicyProtection(require('../PolicyProposal').default);

// Container components for policy features
export { default as PolicyList } from '../containers/PolicyList';
export { default as PolicyForm } from '../containers/PolicyForm';
export { default as PolicySynthesis } from '../containers/PolicySynthesis';

// Presentation components for policy
export { default as PolicyDisplay } from '../presentation/PolicyDisplay';
export { default as PolicyRuleEditor } from '../presentation/PolicyRuleEditor';
export { default as SynthesisProgress } from '../presentation/SynthesisProgress';

// Policy-specific hooks
export { usePolicies } from '../../hooks/usePolicies';
export { usePolicySynthesis } from '../../hooks/usePolicySynthesis';
export { usePolicyValidation } from '../../hooks/usePolicyValidation';

// Policy types
export type {
  Policy,
  PolicyRule,
  ActivePolicy,
  SynthesisRequest,
  SynthesisResult
} from '../../types/governance';
