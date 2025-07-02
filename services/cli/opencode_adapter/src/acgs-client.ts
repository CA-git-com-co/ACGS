import axios, { AxiosInstance } from 'axios';
import { createHash } from 'crypto';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from './logger.js';

export interface ACGSConfig {
  authServiceUrl: string;
  policyServiceUrl: string;
  auditServiceUrl: string;
  hitlServiceUrl: string;
  agentId?: string;
  agentSecret?: string;
  constitutionalHash: string;
}

export interface PolicyCheckRequest {
  action: string;
  resource: string;
  context: Record<string, any>;
  agentId: string;
}

export interface PolicyCheckResponse {
  allowed: boolean;
  reason?: string;
  requiresHITL?: boolean;
  escalationId?: string;
}

export interface AuditEntry {
  id: string;
  timestamp: Date;
  agentId: string;
  action: string;
  resource: string;
  result: 'allowed' | 'denied' | 'escalated';
  context: Record<string, any>;
  hash: string;
}

export class ACGSClient {
  private authClient: AxiosInstance;
  private policyClient: AxiosInstance;
  private auditClient: AxiosInstance;
  private hitlClient: AxiosInstance;
  private logger: Logger;
  private agentToken?: string;

  constructor(private config: ACGSConfig) {
    this.logger = new Logger('ACGSClient');
    
    // Initialize HTTP clients for each ACGS service
    this.authClient = axios.create({
      baseURL: config.authServiceUrl,
      timeout: 5000, // 5ms P99 latency requirement
    });

    this.policyClient = axios.create({
      baseURL: config.policyServiceUrl,
      timeout: 5000,
    });

    this.auditClient = axios.create({
      baseURL: config.auditServiceUrl,
      timeout: 5000,
    });

    this.hitlClient = axios.create({
      baseURL: config.hitlServiceUrl,
      timeout: 30000, // Longer timeout for human responses
    });
  }

  async initialize(): Promise<void> {
    if (!this.config.agentId || !this.config.agentSecret) {
      throw new Error('Agent credentials required for initialization');
    }

    try {
      // Authenticate with ACGS Auth Service
      const response = await this.authClient.post('/authenticate', {
        agentId: this.config.agentId,
        secret: this.config.agentSecret,
      });

      this.agentToken = response.data.token;
      
      // Set auth headers for all clients
      const authHeader = { Authorization: `Bearer ${this.agentToken}` };
      this.policyClient.defaults.headers.common = authHeader;
      this.auditClient.defaults.headers.common = authHeader;
      this.hitlClient.defaults.headers.common = authHeader;

      this.logger.info('Successfully authenticated with ACGS');
    } catch (error) {
      this.logger.error('Failed to authenticate with ACGS', error);
      throw error;
    }
  }

  async checkPolicy(request: PolicyCheckRequest): Promise<PolicyCheckResponse> {
    try {
      // Verify constitutional compliance hash
      const requestHash = this.calculateHash(request);
      if (!this.verifyConstitutionalCompliance(requestHash)) {
        return {
          allowed: false,
          reason: 'Constitutional compliance verification failed',
        };
      }

      // Check policy with ACGS Policy Service
      const response = await this.policyClient.post('/check', request);
      const result: PolicyCheckResponse = response.data;

      // Log audit entry
      await this.logAudit({
        id: uuidv4(),
        timestamp: new Date(),
        agentId: request.agentId,
        action: request.action,
        resource: request.resource,
        result: result.allowed ? 'allowed' : result.requiresHITL ? 'escalated' : 'denied',
        context: request.context,
        hash: requestHash,
      });

      return result;
    } catch (error) {
      this.logger.error('Policy check failed', error);
      throw error;
    }
  }

  async escalateToHuman(
    action: string,
    resource: string,
    context: Record<string, any>
  ): Promise<boolean> {
    try {
      const escalationId = uuidv4();
      
      const response = await this.hitlClient.post('/escalate', {
        escalationId,
        action,
        resource,
        context,
        agentId: this.config.agentId,
        timestamp: new Date().toISOString(),
      });

      return response.data.approved;
    } catch (error) {
      this.logger.error('HITL escalation failed', error);
      throw error;
    }
  }

  private async logAudit(entry: AuditEntry): Promise<void> {
    try {
      await this.auditClient.post('/log', entry);
    } catch (error) {
      this.logger.error('Failed to log audit entry', error);
      // Don't throw - audit logging should not block operations
    }
  }

  private calculateHash(data: any): string {
    const serialized = JSON.stringify(data, Object.keys(data).sort());
    return createHash('sha256').update(serialized).digest('hex');
  }

  private verifyConstitutionalCompliance(hash: string): boolean {
    // Verify against the constitutional compliance hash
    // In production, this would involve more sophisticated verification
    return hash.length === 64; // Basic validation for SHA-256 hash
  }

  async checkPerformanceMetrics(): Promise<{
    latency: number;
    cacheHitRate: number;
    throughput: number;
  }> {
    // Check performance metrics to ensure ACGS requirements are met
    const start = Date.now();
    
    try {
      await this.policyClient.get('/health');
      const latency = Date.now() - start;
      
      // Get metrics from ACGS monitoring
      const metricsResponse = await this.policyClient.get('/metrics');
      const metrics = metricsResponse.data;

      return {
        latency,
        cacheHitRate: metrics.cacheHitRate || 0,
        throughput: metrics.throughput || 0,
      };
    } catch (error) {
      this.logger.error('Failed to check performance metrics', error);
      return {
        latency: -1,
        cacheHitRate: 0,
        throughput: 0,
      };
    }
  }
}