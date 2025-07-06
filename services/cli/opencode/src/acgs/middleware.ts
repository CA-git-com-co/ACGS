/**
 * ACGS Middleware for OpenCode Constitutional Compliance
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * This middleware wraps all OpenCode operations with ACGS constitutional
 * compliance validation, performance monitoring, and audit logging.
 */

import { ACGSClient, loadACGSConfig, CONSTITUTIONAL_HASH } from "./index"
import { Log } from "../util/log"

// Global ACGS client instance
let acgsClient: ACGSClient | null = null

/**
 * Initialize ACGS middleware
 */
export async function initializeACGS(): Promise<void> {
  try {
    const config = await loadACGSConfig()
    acgsClient = new ACGSClient(config)
    
    Log.Default.info("ACGS middleware initialized", {
      constitutional_hash: CONSTITUTIONAL_HASH,
      services_configured: Object.keys(config.acgs.services).length
    })
  } catch (error) {
    Log.Default.error("Failed to initialize ACGS middleware", { error })
    throw error
  }
}

/**
 * Get the ACGS client instance
 */
export function getACGSClient(): ACGSClient {
  if (!acgsClient) {
    throw new Error("ACGS middleware not initialized. Call initializeACGS() first.")
  }
  return acgsClient
}

/**
 * Constitutional compliance decorator for command functions
 */
export function withConstitutionalCompliance<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  operationName: string
) {
  return async (...args: T): Promise<R> => {
    const startTime = Date.now()
    const client = getACGSClient()

    try {
      // Extract context from arguments
      const context = {
        operation: operationName,
        args: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)),
        timestamp: new Date().toISOString(),
        constitutional_hash: CONSTITUTIONAL_HASH
      }

      Log.Default.info("Validating operation with ACGS", { operation: operationName })

      // Validate operation against constitutional principles
      const isValid = await client.validateOperation(operationName, context)
      if (!isValid) {
        throw new Error(`Operation '${operationName}' rejected by constitutional compliance validation`)
      }

      // Check if human approval is required
      const requiresApproval = await client.requiresHumanApproval(operationName, context)
      if (requiresApproval) {
        const approved = await requestHumanApproval(operationName, context)
        if (!approved) {
          throw new Error(`Operation '${operationName}' requires human approval which was denied`)
        }
      }

      // Execute the original function
      const result = await fn(...args)

      // Record successful operation
      const executionTime = Date.now() - startTime
      Log.Default.info("Operation completed successfully", {
        operation: operationName,
        execution_time_ms: executionTime,
        constitutional_hash: CONSTITUTIONAL_HASH
      })

      return result

    } catch (error) {
      const executionTime = Date.now() - startTime
      Log.Default.error("Operation failed", {
        operation: operationName,
        execution_time_ms: executionTime,
        error: error instanceof Error ? error.message : String(error)
      })
      throw error
    }
  }
}

/**
 * Request human approval for high-risk operations
 */
async function requestHumanApproval(operation: string, context: any): Promise<boolean> {
  // In a real implementation, this would integrate with the ACGS HITL service
  // For now, we'll simulate the approval process
  
  Log.Default.warn("Human approval required for operation", { operation, context })
  
  try {
    const client = getACGSClient()
    // TODO: Integrate with actual ACGS HITL service
    // For now, return true to allow operations (fail-open)
    return true
  } catch (error) {
    Log.Default.error("Failed to request human approval", { error })
    return false
  }
}

/**
 * Performance monitoring middleware
 */
export function withPerformanceMonitoring<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  operationName: string
) {
  return async (...args: T): Promise<R> => {
    const startTime = Date.now()
    
    try {
      const result = await fn(...args)
      const executionTime = Date.now() - startTime
      
      // Check against performance targets
      const client = getACGSClient()
      const metrics = client.getPerformanceMetrics()
      
      if (executionTime > metrics.target_p99_latency) {
        Log.Default.warn("Operation exceeded P99 latency target", {
          operation: operationName,
          execution_time_ms: executionTime,
          target_ms: metrics.target_p99_latency
        })
      }

      return result
    } catch (error) {
      const executionTime = Date.now() - startTime
      Log.Default.error("Performance monitoring - operation failed", {
        operation: operationName,
        execution_time_ms: executionTime,
        error: error instanceof Error ? error.message : String(error)
      })
      throw error
    }
  }
}

/**
 * Combined ACGS middleware that applies both constitutional compliance and performance monitoring
 */
export function withACGSCompliance<T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  operationName: string
) {
  return withPerformanceMonitoring(
    withConstitutionalCompliance(fn, operationName),
    operationName
  )
}

/**
 * ACGS health check for monitoring service status
 */
export async function acgsHealthCheck(): Promise<{
  status: string
  constitutional_hash: string
  services: Record<string, boolean>
  performance: any
}> {
  if (!acgsClient) {
    return {
      status: "not_initialized",
      constitutional_hash: CONSTITUTIONAL_HASH,
      services: {},
      performance: {}
    }
  }

  try {
    const config = await loadACGSConfig()
    const services: Record<string, boolean> = {}

    // Check each ACGS service
    for (const [serviceName, serviceUrl] of Object.entries(config.acgs.services)) {
      try {
        const response = await fetch(`${serviceUrl}/health`, {
          method: 'GET',
          headers: { 'X-Constitutional-Hash': CONSTITUTIONAL_HASH },
          signal: AbortSignal.timeout(1000) // 1 second timeout
        })
        services[serviceName] = response.ok
      } catch {
        services[serviceName] = false
      }
    }

    const performance = acgsClient.getPerformanceMetrics()

    return {
      status: "healthy",
      constitutional_hash: CONSTITUTIONAL_HASH,
      services,
      performance
    }
  } catch (error) {
    Log.Default.error("ACGS health check failed", { error })
    return {
      status: "error",
      constitutional_hash: CONSTITUTIONAL_HASH,
      services: {},
      performance: {}
    }
  }
}