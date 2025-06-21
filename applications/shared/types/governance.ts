// ACGS-PGP Framework Types
//
// This file maintains backward compatibility while providing enhanced
// type definitions with runtime validation support via Zod schemas.

import { z } from 'zod';
import {
  UserSchema,
  PrincipleSchema,
  PolicySchema,
  PolicyRuleSchema,
  ActivePolicySchema,
  ComplianceResultSchema,
  AmendmentSchema,
  AmendmentVoteSchema,
  SynthesisRequestSchema,
  SynthesisResultSchema
} from './validation';

/**
 * Principle interface for Artificial Constitution (AC)
 *
 * @example
 * ```typescript
 * const principle: Principle = {
 *   id: "PRIN-001",
 *   title: "Democratic Governance",
 *   content: "All policy changes must be approved through democratic voting",
 *   category: "governance",
 *   priority: 9
 * };
 * ```
 */
export interface Principle {
  /** Unique principle identifier */
  id: string;
  /** Principle title */
  title: string;
  /** Principle content/description */
  content: string;
  /** Principle category */
  category: string;
  /** Priority level (1-10, higher is more important) */
  priority: number;
  /** Creation timestamp */
  createdAt?: Date;
  /** Last update timestamp */
  updatedAt?: Date;
  /** Author identifier */
  author?: string;
}

/**
 * Policy interface for Self-Synthesizing (GS) Engine
 *
 * @example
 * ```typescript
 * const policy: Policy = {
 *   id: "POL-001",
 *   name: "Treasury Protection",
 *   description: "Protects treasury funds from unauthorized access",
 *   rules: [{ id: "R1", condition: "amount > limit", action: "DENY" }],
 *   validationScore: 95,
 *   complianceComplexity: 30,
 *   status: "active",
 *   category: "financial",
 *   createdAt: new Date(),
 *   updatedAt: new Date(),
 *   author: "system"
 * };
 * ```
 */
export interface Policy {
  /** Unique policy identifier */
  id: string;
  /** Policy name */
  name: string;
  /** Policy description */
  description: string;
  /** Policy rules */
  rules: PolicyRule[];
  /** Validation score (0-100) */
  validationScore: number;
  /** Compliance complexity score (0-100) */
  complianceComplexity: number;
  /** Policy status */
  status: 'draft' | 'active' | 'archived';
  /** Policy category */
  category: string;
  /** Creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
  /** Author identifier */
  author: string;
}

/**
 * Policy rule interface
 *
 * @example
 * ```typescript
 * const rule: PolicyRule = {
 *   id: "RULE-001",
 *   condition: "user.role !== 'admin'",
 *   action: "REQUIRE approval"
 * };
 * ```
 */
export interface PolicyRule {
  /** Rule identifier */
  id: string;
  /** Condition that triggers the rule */
  condition: string;
  /** Action to take when condition is met */
  action: string;
}

// Compliance types for Prompt Governance Compiler (PGC)
export interface ComplianceResult {
  compliant: boolean;
  confidenceScore: number;
  violationReasons?: string[];
}

export interface ActivePolicy {
  id: string;
  name: string;
  rules: PolicyRule[];
}

// Amendment types
export interface Amendment {
  id: string;
  title: string;
  description: string;
  proposer: string;
  status: 'pending' | 'voting' | 'approved' | 'rejected';
  votingDeadline?: Date;
  createdAt: Date;
  votes?: AmendmentVote[];
}

export interface AmendmentVote {
  id: string;
  amendmentId: string;
  userId: string;
  vote: 'yes' | 'no' | 'abstain';
  comment?: string;
  createdAt: Date;
}

// Synthesis types for GS Engine
export interface SynthesisRequest {
  principles: { id: string }[];
}

export interface SynthesisResult {
  policies: Policy[];
  validationScore: number;
  complianceComplexity: number;
}

// User and Authentication types
export interface User {
  id: string;
  username: string;
  email?: string;
  role: string;
  createdAt?: Date;
}

export interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// Legacy types for backward compatibility
export interface Proposal {
  id: string;
  title: string;
  description: string;
  proposer: string;
  status: 'pending' | 'voting' | 'approved' | 'rejected';
  votingDeadline: Date;
  createdAt: Date;
  votes: Vote[];
}

export interface Vote {
  id: string;
  proposalId: string;
  userId: string;
  vote: 'yes' | 'no' | 'abstain';
  comment?: string;
  createdAt: Date;
}

export interface DashboardCard {
  id: string;
  title: string;
  content: React.ReactNode;
  position: number;
  size: 'small' | 'medium' | 'large';
}
