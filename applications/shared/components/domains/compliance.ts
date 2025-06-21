// Compliance Domain Components (PGC Service)
//
// Components related to compliance checking, validation,
// and enforcement managed by the PGC service.

import { withPGCProtection, withComplianceProtection } from '../hoc/composite';

// Re-export compliance-related components
export { default as ComplianceChecker } from '../ComplianceChecker';

// Protected versions of compliance components
export const ProtectedComplianceChecker = withComplianceProtection(
  require('../ComplianceChecker').default
);

// Container components for compliance features
export { default as ComplianceMonitor } from '../containers/ComplianceMonitor';
export { default as ViolationTracker } from '../containers/ViolationTracker';
export { default as ComplianceReports } from '../containers/ComplianceReports';

// Presentation components for compliance
export { default as ComplianceResult } from '../presentation/ComplianceResult';
export { default as ViolationAlert } from '../presentation/ViolationAlert';
export { default as ComplianceMetrics } from '../presentation/ComplianceMetrics';

// Compliance-specific hooks
export { useCompliance } from '../../hooks/useCompliance';
export { useComplianceHistory } from '../../hooks/useComplianceHistory';
export { useViolationTracking } from '../../hooks/useViolationTracking';

// Compliance types
export type { ComplianceResult } from '../../types/governance';
