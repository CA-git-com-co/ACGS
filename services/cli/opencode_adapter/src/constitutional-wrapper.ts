import { createHash } from 'crypto';
import { Logger } from './logger.js';

export interface ConstitutionalPrinciple {
  id: string;
  name: string;
  description: string;
  validator: (context: any) => boolean;
}

export interface ComplianceCheckResult {
  compliant: boolean;
  violations: string[];
  hash: string;
  timestamp: Date;
}

export class ConstitutionalWrapper {
  private logger: Logger;
  private principles: Map<string, ConstitutionalPrinciple>;
  private constitutionalHash: string;

  constructor(constitutionalHash: string) {
    this.logger = new Logger('ConstitutionalWrapper');
    this.constitutionalHash = constitutionalHash;
    this.principles = new Map();
    this.initializePrinciples();
  }

  private initializePrinciples(): void {
    // Core ACGS constitutional principles
    const principles: ConstitutionalPrinciple[] = [
      {
        id: 'safety',
        name: 'Safety First',
        description: 'Operations must not cause harm to systems or data',
        validator: (context) => {
          // Check for potentially harmful operations
          const dangerousOps = ['rm -rf', 'format', 'delete', 'drop database', 'truncate'];
          const operation = context.operation?.toLowerCase() || '';
          return !dangerousOps.some(op => operation.includes(op));
        },
      },
      {
        id: 'transparency',
        name: 'Operational Transparency',
        description: 'All operations must be logged and auditable',
        validator: (context) => {
          return context.requestId && context.timestamp && context.agentId;
        },
      },
      {
        id: 'consent',
        name: 'User Consent',
        description: 'High-risk operations require explicit user consent',
        validator: (context) => {
          const highRiskOps = ['production', 'customer-data', 'financial'];
          const requiresConsent = highRiskOps.some(op => 
            context.resource?.includes(op) || context.tags?.includes(op)
          );
          return !requiresConsent || context.userConsent === true;
        },
      },
      {
        id: 'data-privacy',
        name: 'Data Privacy',
        description: 'Personal and sensitive data must be protected',
        validator: (context) => {
          const sensitivePatterns = [
            /ssn|social.?security/i,
            /credit.?card/i,
            /password/i,
            /api.?key/i,
            /secret/i,
            /private.?key/i,
          ];
          
          const data = JSON.stringify(context);
          return !sensitivePatterns.some(pattern => pattern.test(data));
        },
      },
      {
        id: 'resource-limits',
        name: 'Resource Constraints',
        description: 'Operations must respect system resource limits',
        validator: (context) => {
          const limits = {
            maxMemoryMB: 1024,
            maxCPUPercent: 80,
            maxDurationMs: 30000,
          };
          
          return (
            (!context.estimatedMemoryMB || context.estimatedMemoryMB <= limits.maxMemoryMB) &&
            (!context.estimatedCPU || context.estimatedCPU <= limits.maxCPUPercent) &&
            (!context.estimatedDurationMs || context.estimatedDurationMs <= limits.maxDurationMs)
          );
        },
      },
      {
        id: 'reversibility',
        name: 'Operation Reversibility',
        description: 'Destructive operations must be reversible or have backups',
        validator: (context) => {
          const destructiveOps = ['delete', 'remove', 'drop', 'truncate', 'overwrite'];
          const isDestructive = destructiveOps.some(op => 
            context.operation?.toLowerCase().includes(op)
          );
          
          return !isDestructive || (context.hasBackup === true || context.isReversible === true);
        },
      },
      {
        id: 'least-privilege',
        name: 'Least Privilege',
        description: 'Operations must use minimum required permissions',
        validator: (context) => {
          const privilegedOps = ['sudo', 'admin', 'root', 'superuser'];
          const operation = context.operation?.toLowerCase() || '';
          const usesPrivileged = privilegedOps.some(op => operation.includes(op));
          
          return !usesPrivileged || context.privilegedJustification;
        },
      },
    ];

    // Register all principles
    principles.forEach(principle => {
      this.principles.set(principle.id, principle);
    });
  }

  async checkCompliance(
    operation: string,
    context: Record<string, any>
  ): Promise<ComplianceCheckResult> {
    const checkContext = {
      ...context,
      operation,
      timestamp: new Date().toISOString(),
    };

    const violations: string[] = [];
    
    // Check each constitutional principle
    for (const [id, principle] of this.principles) {
      try {
        const compliant = principle.validator(checkContext);
        if (!compliant) {
          violations.push(`${principle.name}: ${principle.description}`);
          this.logger.warn('Constitutional principle violated', {
            principleId: id,
            principle: principle.name,
            operation,
          });
        }
      } catch (error) {
        this.logger.error(`Failed to check principle ${id}`, error);
        violations.push(`${principle.name}: Validation error`);
      }
    }

    // Calculate compliance hash
    const hash = this.calculateComplianceHash(checkContext, violations);

    const result: ComplianceCheckResult = {
      compliant: violations.length === 0,
      violations,
      hash,
      timestamp: new Date(),
    };

    // Log compliance check result
    this.logger.info('Constitutional compliance check completed', {
      operation,
      compliant: result.compliant,
      violationCount: violations.length,
      hash: result.hash,
    });

    return result;
  }

  private calculateComplianceHash(context: any, violations: string[]): string {
    const data = {
      context,
      violations,
      constitutionalHash: this.constitutionalHash,
      timestamp: new Date().toISOString(),
    };

    return createHash('sha256')
      .update(JSON.stringify(data))
      .digest('hex');
  }

  // Add a new constitutional principle at runtime
  addPrinciple(principle: ConstitutionalPrinciple): void {
    this.principles.set(principle.id, principle);
    this.logger.info('Added new constitutional principle', {
      principleId: principle.id,
      name: principle.name,
    });
  }

  // Remove a principle (use with caution)
  removePrinciple(principleId: string): boolean {
    const removed = this.principles.delete(principleId);
    if (removed) {
      this.logger.warn('Removed constitutional principle', { principleId });
    }
    return removed;
  }

  // Get all registered principles
  getPrinciples(): ConstitutionalPrinciple[] {
    return Array.from(this.principles.values());
  }

  // Verify the constitutional hash matches expected value
  verifyConstitutionalHash(): boolean {
    const currentHash = createHash('sha256')
      .update(JSON.stringify(this.getPrinciples().map(p => ({
        id: p.id,
        name: p.name,
        description: p.description,
      }))))
      .digest('hex')
      .substring(0, 16); // Use first 16 chars like the original hash

    return currentHash === this.constitutionalHash;
  }
}