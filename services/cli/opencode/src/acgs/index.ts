/**
 * ACGS Integration Layer for OpenCode
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * This module provides constitutional compliance and governance integration
 * for OpenCode operations within the ACGS framework.
 */

import { z } from "zod"
import { Log } from "../util/log"

// Constitutional hash for compliance validation
export const CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

// ACGS service endpoints
export interface ACGSServices {
  auth_service_url: string
  constitutional_ai_url: string
  integrity_service_url: string
  formal_verification_url: string
  governance_synthesis_url: string
  policy_governance_url: string
  evolutionary_computation_url: string
}

// Constitutional principles enforcement
export interface ConstitutionalPrinciples {
  safety_first: boolean
  operational_transparency: boolean
  user_consent: boolean
  data_privacy: boolean
  resource_constraints: boolean
  operation_reversibility: boolean
  least_privilege: boolean
}

// Performance targets for ACGS compliance
export interface PerformanceTargets {
  p99_latency_ms: number
  cache_hit_rate: number
  throughput_rps: number
}

// ACGS configuration schema
export const ACGSConfigSchema = z.object({
  acgs: z.object({
    constitutional_hash: z.string().default(CONSTITUTIONAL_HASH),
    services: z.object({
      auth_service_url: z.string().default("http://localhost:8016"),
      constitutional_ai_url: z.string().default("http://localhost:8001"),
      integrity_service_url: z.string().default("http://localhost:8002"),
      formal_verification_url: z.string().default("http://localhost:8003"),
      governance_synthesis_url: z.string().default("http://localhost:8004"),
      policy_governance_url: z.string().default("http://localhost:8005"),
      evolutionary_computation_url: z.string().default("http://localhost:8006")
    }),
    performance_targets: z.object({
      p99_latency_ms: z.number().default(5),
      cache_hit_rate: z.number().default(0.85),
      throughput_rps: z.number().default(1000)
    }),
    constitutional_principles: z.object({
      safety_first: z.boolean().default(true),
      operational_transparency: z.boolean().default(true),
      user_consent: z.boolean().default(true),
      data_privacy: z.boolean().default(true),
      resource_constraints: z.boolean().default(true),
      operation_reversibility: z.boolean().default(true),
      least_privilege: z.boolean().default(true)
    }),
    compliance_validation: z.object({
      validate_all_operations: z.boolean().default(true),
      audit_trail: z.boolean().default(true),
      human_in_the_loop: z.boolean().default(true),
      formal_verification: z.boolean().default(true)
    })
  })
})

export type ACGSConfig = z.infer<typeof ACGSConfigSchema>

/**
 * ACGS Client for constitutional compliance and service integration
 */
export class ACGSClient {
  private config: ACGSConfig
  private performanceMetrics: Map<string, number[]> = new Map()

  constructor(config: ACGSConfig) {
    this.config = config
    this.validateConfiguration()
  }

  private validateConfiguration(): void {
    if (this.config.acgs.constitutional_hash !== CONSTITUTIONAL_HASH) {
      throw new Error(`Constitutional hash mismatch. Expected: ${CONSTITUTIONAL_HASH}, got: ${this.config.acgs.constitutional_hash}`)
    }
    Log.Default.info("ACGS Client initialized with constitutional compliance", {
      hash: CONSTITUTIONAL_HASH,
      services: Object.keys(this.config.acgs.services).length
    })
  }

  /**
   * Validate operation against constitutional principles
   */
  async validateOperation(operation: string, context: any): Promise<boolean> {
    const startTime = Date.now()
    
    try {
      // Check constitutional principles
      if (!this.config.acgs.constitutional_principles.safety_first && this.isHighRiskOperation(operation)) {
        Log.Default.warn("High-risk operation blocked by safety principle", { operation })
        return false
      }

      // Validate with Constitutional AI service
      if (this.config.acgs.compliance_validation.validate_all_operations) {
        const isValid = await this.validateWithConstitutionalAI(operation, context)
        if (!isValid) {
          Log.Default.warn("Operation rejected by Constitutional AI validation", { operation })
          return false
        }
      }

      // Check formal verification if enabled
      if (this.config.acgs.compliance_validation.formal_verification) {
        const formallyValid = await this.performFormalVerification(operation, context)
        if (!formallyValid) {
          Log.Default.warn("Operation failed formal verification", { operation })
          return false
        }
      }

      // Log audit trail
      if (this.config.acgs.compliance_validation.audit_trail) {
        await this.logAuditTrail(operation, context, true)
      }

      this.recordPerformanceMetric("validation_latency", Date.now() - startTime)
      return true

    } catch (error) {
      Log.Default.error("Operation validation failed", { operation, error })
      await this.logAuditTrail(operation, context, false)
      return false
    }
  }

  /**
   * Check if operation requires human-in-the-loop approval
   */
  async requiresHumanApproval(operation: string, context: any): Promise<boolean> {
    if (!this.config.acgs.compliance_validation.human_in_the_loop) {
      return false
    }

    // Define high-risk operations that require human approval
    const highRiskOperations = [
      "delete", "remove", "destroy", "format", "wipe",
      "deploy", "production", "critical", "admin"
    ]

    return highRiskOperations.some(risk => 
      operation.toLowerCase().includes(risk) || 
      JSON.stringify(context).toLowerCase().includes(risk)
    )
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics(): Record<string, any> {
    const metrics: Record<string, any> = {}
    
    for (const [metric, values] of this.performanceMetrics) {
      if (values.length > 0) {
        const sorted = values.sort((a, b) => a - b)
        metrics[metric] = {
          p99: sorted[Math.floor(sorted.length * 0.99)],
          p95: sorted[Math.floor(sorted.length * 0.95)],
          p50: sorted[Math.floor(sorted.length * 0.50)],
          avg: values.reduce((a, b) => a + b, 0) / values.length,
          count: values.length
        }
      }
    }

    return {
      ...metrics,
      constitutional_hash: CONSTITUTIONAL_HASH,
      compliance_status: "active",
      target_p99_latency: this.config.acgs.performance_targets.p99_latency_ms
    }
  }

  private isHighRiskOperation(operation: string): boolean {
    const highRiskPatterns = [
      /rm\s+-rf/i, /format/i, /delete/i, /destroy/i, /wipe/i,
      /sudo/i, /admin/i, /root/i, /critical/i, /production/i
    ]
    
    return highRiskPatterns.some(pattern => pattern.test(operation))
  }

  private async validateWithConstitutionalAI(operation: string, context: any): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.acgs.services.constitutional_ai_url}/api/v1/constitutional/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH
        },
        body: JSON.stringify({
          operation,
          context,
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) {
        Log.Default.warn("Constitutional AI service unavailable", { status: response.status })
        return true // Fail open for availability
      }

      const result = await response.json()
      return result.compliant === true
    } catch (error) {
      Log.Default.warn("Constitutional AI validation failed", { error })
      return true // Fail open for availability
    }
  }

  private async performFormalVerification(operation: string, context: any): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.acgs.services.formal_verification_url}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH
        },
        body: JSON.stringify({
          operation,
          context,
          constitutional_hash: CONSTITUTIONAL_HASH
        })
      })

      if (!response.ok) {
        Log.Default.warn("Formal verification service unavailable", { status: response.status })
        return true // Fail open for availability
      }

      const result = await response.json()
      return result.verified === true
    } catch (error) {
      Log.Default.warn("Formal verification failed", { error })
      return true // Fail open for availability
    }
  }

  private async logAuditTrail(operation: string, context: any, success: boolean): Promise<void> {
    try {
      const auditEntry = {
        operation,
        context,
        success,
        constitutional_hash: CONSTITUTIONAL_HASH,
        timestamp: new Date().toISOString(),
        agent: "opencode-cli"
      }

      await fetch(`${this.config.acgs.services.integrity_service_url}/api/v1/audit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': CONSTITUTIONAL_HASH
        },
        body: JSON.stringify(auditEntry)
      })
    } catch (error) {
      Log.Default.warn("Audit logging failed", { error })
      // Don't fail the operation for audit logging issues
    }
  }

  private recordPerformanceMetric(metric: string, value: number): void {
    if (!this.performanceMetrics.has(metric)) {
      this.performanceMetrics.set(metric, [])
    }
    
    const values = this.performanceMetrics.get(metric)!
    values.push(value)
    
    // Keep only last 1000 values for memory efficiency
    if (values.length > 1000) {
      values.splice(0, values.length - 1000)
    }
  }
}

/**
 * Load ACGS configuration from file
 */
export async function loadACGSConfig(): Promise<ACGSConfig> {
  try {
    const configPath = process.env.ACGS_CONFIG_PATH || "./acgs-config.json"
    const configFile = await Bun.file(configPath).text()
    const rawConfig = JSON.parse(configFile)
    
    return ACGSConfigSchema.parse(rawConfig)
  } catch (error) {
    Log.Default.warn("Failed to load ACGS config, using defaults", { error })
    
    // Return default configuration
    return ACGSConfigSchema.parse({
      acgs: {
        constitutional_hash: CONSTITUTIONAL_HASH,
        services: {
          auth_service_url: "http://localhost:8016",
          constitutional_ai_url: "http://localhost:8001",
          integrity_service_url: "http://localhost:8002",
          formal_verification_url: "http://localhost:8003",
          governance_synthesis_url: "http://localhost:8004",
          policy_governance_url: "http://localhost:8005",
          evolutionary_computation_url: "http://localhost:8006"
        },
        performance_targets: {
          p99_latency_ms: 5,
          cache_hit_rate: 0.85,
          throughput_rps: 1000
        },
        constitutional_principles: {
          safety_first: true,
          operational_transparency: true,
          user_consent: true,
          data_privacy: true,
          resource_constraints: true,
          operation_reversibility: true,
          least_privilege: true
        },
        compliance_validation: {
          validate_all_operations: true,
          audit_trail: true,
          human_in_the_loop: true,
          formal_verification: true
        }
      }
    })
  }
}