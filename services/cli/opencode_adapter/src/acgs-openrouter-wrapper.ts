import { EventEmitter } from 'events';
import { ACGSClient, PolicyCheckRequest } from './acgs-client.js';
import { ConstitutionalWrapper, ComplianceCheckResult } from './constitutional-wrapper.js';
import { PerformanceMonitor } from './performance-monitor.js';
import { OpenRouterProvider, ModelInfo } from './providers/openrouter-provider.js';
import { Logger } from './logger.js';

export interface ACGSOpenRouterConfig {
  openRouterApiKey: string;
  constitutionalHash: string;
  defaultModel?: string;
  enableCostOptimization?: boolean;
  maxCostPerRequest?: number; // USD
  performanceTargets?: {
    maxLatencyMs?: number;
    minCacheHitRate?: number;
  };
}

export interface CodeRequest {
  task: 'generate' | 'review' | 'explain' | 'optimize';
  prompt?: string;
  code?: string;
  language?: string;
  model?: string;
  context?: Record<string, any>;
  requirements?: string[];
  agentId: string;
  requestId: string;
}

export interface CodeResponse {
  success: boolean;
  result?: {
    code?: string;
    explanation?: string;
    review?: any;
    optimization?: any;
  };
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    estimatedCost: number;
  };
  compliance: ComplianceCheckResult;
  performance: {
    latency: number;
    cacheHit: boolean;
  };
  error?: string;
}

export class ACGSOpenRouterWrapper extends EventEmitter {
  private acgsClient: ACGSClient;
  private constitutionalWrapper: ConstitutionalWrapper;
  private performanceMonitor: PerformanceMonitor;
  private openRouterProvider: OpenRouterProvider;
  private logger: Logger;
  private config: Required<ACGSOpenRouterConfig>;
  private requestCache: Map<string, CodeResponse> = new Map();
  private modelCostCache: Map<string, ModelInfo> = new Map();

  constructor(acgsClient: ACGSClient, config: ACGSOpenRouterConfig) {
    super();
    
    this.config = {
      defaultModel: 'anthropic/claude-3.5-sonnet',
      enableCostOptimization: true,
      maxCostPerRequest: 0.10, // $0.10 per request
      performanceTargets: {
        maxLatencyMs: 5000,
        minCacheHitRate: 0.85,
      },
      ...config,
    };

    this.acgsClient = acgsClient;
    this.constitutionalWrapper = new ConstitutionalWrapper(config.constitutionalHash);
    this.performanceMonitor = new PerformanceMonitor();
    this.logger = new Logger('ACGSOpenRouterWrapper');

    this.openRouterProvider = new OpenRouterProvider({
      apiKey: config.openRouterApiKey,
      defaultModel: this.config.defaultModel,
    });
  }

  async initialize(): Promise<void> {
    try {
      await this.acgsClient.initialize();
      this.performanceMonitor.start();
      
      // Load model costs for optimization
      await this.loadModelCosts();
      
      this.logger.info('ACGS OpenRouter wrapper initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize ACGS OpenRouter wrapper', error);
      throw error;
    }
  }

  async processRequest(request: CodeRequest): Promise<CodeResponse> {
    const startTime = Date.now();
    let cacheHit = false;

    try {
      // Generate cache key
      const cacheKey = this.generateCacheKey(request);
      
      // Check cache first
      if (this.requestCache.has(cacheKey)) {
        const cached = this.requestCache.get(cacheKey)!;
        this.performanceMonitor.recordCacheHit();
        this.performanceMonitor.recordMetric('request_latency', Date.now() - startTime);
        cacheHit = true;
        
        return {
          ...cached,
          performance: {
            latency: Date.now() - startTime,
            cacheHit: true,
          },
        };
      }

      this.performanceMonitor.recordCacheMiss();

      // Step 1: Constitutional compliance check
      const complianceResult = await this.checkConstitutionalCompliance(request);
      if (!complianceResult.compliant) {
        return this.createErrorResponse(
          request,
          `Constitutional compliance failed: ${complianceResult.violations.join('; ')}`,
          complianceResult,
          Date.now() - startTime,
          cacheHit
        );
      }

      // Step 2: ACGS policy check
      const policyAllowed = await this.checkACGSPolicy(request);
      if (!policyAllowed.allowed) {
        if (policyAllowed.requiresHITL) {
          const humanApproved = await this.escalateToHuman(request);
          if (!humanApproved) {
            return this.createErrorResponse(
              request,
              'Human-in-the-loop rejected the request',
              complianceResult,
              Date.now() - startTime,
              cacheHit
            );
          }
        } else {
          return this.createErrorResponse(
            request,
            policyAllowed.reason || 'Policy check failed',
            complianceResult,
            Date.now() - startTime,
            cacheHit
          );
        }
      }

      // Step 3: Model selection and cost optimization
      const selectedModel = await this.selectOptimalModel(request);
      
      // Step 4: Cost check
      const estimatedCost = await this.estimateRequestCost(request, selectedModel);
      if (estimatedCost > this.config.maxCostPerRequest) {
        return this.createErrorResponse(
          request,
          `Request cost ${estimatedCost.toFixed(4)} USD exceeds limit ${this.config.maxCostPerRequest} USD`,
          complianceResult,
          Date.now() - startTime,
          cacheHit
        );
      }

      // Step 5: Execute the AI operation
      const result = await this.executeAIOperation(request, selectedModel);

      // Step 6: Performance validation
      const latency = Date.now() - startTime;
      if (latency > (this.config.performanceTargets.maxLatencyMs || 5000)) {
        this.logger.warn('Request exceeded latency target', {
          latency,
          target: this.config.performanceTargets.maxLatencyMs,
        });
      }

      const response: CodeResponse = {
        success: true,
        result,
        model: selectedModel,
        usage: {
          promptTokens: result.usage?.promptTokens || 0,
          completionTokens: result.usage?.completionTokens || 0,
          totalTokens: result.usage?.totalTokens || 0,
          estimatedCost,
        },
        compliance: complianceResult,
        performance: {
          latency,
          cacheHit,
        },
      };

      // Cache the response
      this.requestCache.set(cacheKey, response);
      this.performanceMonitor.recordMetric('request_latency', latency);

      // Emit events for monitoring
      this.emit('request_completed', {
        requestId: request.requestId,
        task: request.task,
        model: selectedModel,
        latency,
        cost: estimatedCost,
        success: true,
      });

      return response;

    } catch (error) {
      const latency = Date.now() - startTime;
      this.logger.error('Failed to process request', error);
      
      this.emit('request_failed', {
        requestId: request.requestId,
        task: request.task,
        error: error instanceof Error ? error.message : 'Unknown error',
        latency,
      });

      return this.createErrorResponse(
        request,
        error instanceof Error ? error.message : 'Unknown error occurred',
        { compliant: false, violations: ['System error'], hash: '', timestamp: new Date() },
        latency,
        cacheHit
      );
    }
  }

  private async checkConstitutionalCompliance(request: CodeRequest): Promise<ComplianceCheckResult> {
    const context = {
      task: request.task,
      prompt: request.prompt,
      code: request.code,
      language: request.language,
      agentId: request.agentId,
      requestId: request.requestId,
      timestamp: new Date().toISOString(),
      ...request.context,
    };

    return await this.constitutionalWrapper.checkCompliance(
      `openrouter:${request.task}`,
      context
    );
  }

  private async checkACGSPolicy(request: CodeRequest): Promise<{
    allowed: boolean;
    reason?: string;
    requiresHITL?: boolean;
  }> {
    const policyRequest: PolicyCheckRequest = {
      action: `ai:${request.task}`,
      resource: 'openrouter-api',
      context: {
        model: request.model,
        language: request.language,
        prompt: request.prompt?.substring(0, 100), // First 100 chars for context
        agentId: request.agentId,
        requestId: request.requestId,
      },
      agentId: request.agentId,
    };

    try {
      const result = await this.acgsClient.checkPolicy(policyRequest);
      return {
        allowed: result.allowed,
        reason: result.reason,
        requiresHITL: result.requiresHITL,
      };
    } catch (error) {
      this.logger.error('Policy check failed', error);
      return { allowed: false, reason: 'Policy service unavailable' };
    }
  }

  private async escalateToHuman(request: CodeRequest): Promise<boolean> {
    try {
      return await this.acgsClient.escalateToHuman(
        `ai:${request.task}`,
        'openrouter-api',
        {
          task: request.task,
          model: request.model,
          language: request.language,
          requestId: request.requestId,
        }
      );
    } catch (error) {
      this.logger.error('HITL escalation failed', error);
      return false;
    }
  }

  private async selectOptimalModel(request: CodeRequest): Promise<string> {
    if (request.model) {
      return request.model; // Use explicitly requested model
    }

    if (!this.config.enableCostOptimization) {
      return this.config.defaultModel;
    }

    try {
      return await this.openRouterProvider.selectOptimalModel(
        request.task as any,
        {
          costPriority: 'balanced',
          language: request.language,
          complexity: this.assessComplexity(request),
        }
      );
    } catch (error) {
      this.logger.warn('Model selection failed, using default', error);
      return this.config.defaultModel;
    }
  }

  private async estimateRequestCost(request: CodeRequest, model: string): Promise<number> {
    const modelInfo = this.modelCostCache.get(model);
    if (!modelInfo) {
      return 0.001; // Default estimate
    }

    const promptLength = (request.prompt || '').length + (request.code || '').length;
    const estimatedPromptTokens = Math.ceil(promptLength / 4); // Rough estimate
    const estimatedCompletionTokens = request.task === 'explain' ? 500 : 1000;

    return (estimatedPromptTokens * modelInfo.cost.input) + 
           (estimatedCompletionTokens * modelInfo.cost.output);
  }

  private async executeAIOperation(request: CodeRequest, model: string): Promise<any> {
    const options = {
      language: request.language,
      model,
      context: request.context,
    };

    switch (request.task) {
      case 'generate':
        if (!request.prompt) throw new Error('Prompt required for code generation');
        return await this.openRouterProvider.generateCode(request.prompt, {
          ...options,
          requirements: request.requirements,
        });

      case 'review':
        if (!request.code) throw new Error('Code required for review');
        return await this.openRouterProvider.reviewCode(request.code, options);

      case 'explain':
        if (!request.code) throw new Error('Code required for explanation');
        const explanation = await this.openRouterProvider.explainCode(request.code, options);
        return { explanation, usage: { promptTokens: 0, completionTokens: 0, totalTokens: 0 } };

      case 'optimize':
        if (!request.code) throw new Error('Code required for optimization');
        return await this.openRouterProvider.optimizeCode(request.code, {
          ...options,
          optimizationGoals: request.requirements,
        });

      default:
        throw new Error(`Unsupported task: ${request.task}`);
    }
  }

  private assessComplexity(request: CodeRequest): 'low' | 'medium' | 'high' {
    const contentLength = (request.prompt || '').length + (request.code || '').length;
    
    if (contentLength > 2000 || request.requirements && request.requirements.length > 3) {
      return 'high';
    } else if (contentLength > 500 || request.requirements && request.requirements.length > 1) {
      return 'medium';
    }
    
    return 'low';
  }

  private generateCacheKey(request: CodeRequest): string {
    const keyData = {
      task: request.task,
      prompt: request.prompt,
      code: request.code,
      language: request.language,
      model: request.model,
      requirements: request.requirements,
    };
    
    return Buffer.from(JSON.stringify(keyData)).toString('base64');
  }

  private async loadModelCosts(): Promise<void> {
    try {
      const models = await this.openRouterProvider.getAvailableModels();
      this.modelCostCache.clear();
      models.forEach(model => {
        this.modelCostCache.set(model.id, model);
      });
      
      this.logger.info('Loaded cost information for models', { count: models.length });
    } catch (error) {
      this.logger.warn('Failed to load model costs', error);
    }
  }

  private createErrorResponse(
    request: CodeRequest,
    error: string,
    compliance: ComplianceCheckResult,
    latency: number,
    cacheHit: boolean
  ): CodeResponse {
    return {
      success: false,
      model: request.model || this.config.defaultModel,
      usage: {
        promptTokens: 0,
        completionTokens: 0,
        totalTokens: 0,
        estimatedCost: 0,
      },
      compliance,
      performance: { latency, cacheHit },
      error,
    };
  }

  async getPerformanceMetrics() {
    return {
      ...this.performanceMonitor.getMetrics(),
      cacheSize: this.requestCache.size,
      modelsCached: this.modelCostCache.size,
    };
  }

  async shutdown(): Promise<void> {
    this.performanceMonitor.stop();
    this.requestCache.clear();
    this.modelCostCache.clear();
    this.logger.info('ACGS OpenRouter wrapper shut down');
  }
}