import { EventEmitter } from 'events';
import { ACGSClient, PolicyCheckRequest } from './acgs-client.js';
import { Logger } from './logger.js';
import { PerformanceMonitor } from './performance-monitor.js';
import { ConstitutionalWrapper } from './constitutional-wrapper.js';
import { OpenRouterClient, CodeRequest } from './openrouter-client.js';

export interface OpenCodeCommand {
  command: string;
  args: string[];
  context: Record<string, any>;
  prompt?: string;
  language?: string;
  model?: string;
}

export interface OpenCodeResult {
  success: boolean;
  output?: string;
  error?: string;
  performanceMetrics?: {
    latency: number;
    memoryUsage: number;
  };
}

export class OpenCodeAdapter extends EventEmitter {
  private acgsClient: ACGSClient;
  private logger: Logger;
  private performanceMonitor: PerformanceMonitor;
  private constitutionalWrapper: ConstitutionalWrapper;
  private openRouterClient: OpenRouterClient;
  private isInitialized = false;

  constructor(
    acgsClient: ACGSClient, 
    constitutionalHash: string,
    openRouterConfig: { apiKey: string; defaultModel?: string }
  ) {
    super();
    this.acgsClient = acgsClient;
    this.logger = new Logger('OpenCodeAdapter');
    this.performanceMonitor = new PerformanceMonitor();
    this.constitutionalWrapper = new ConstitutionalWrapper(constitutionalHash);
    this.openRouterClient = new OpenRouterClient({
      apiKey: openRouterConfig.apiKey,
      defaultModel: openRouterConfig.defaultModel || 'anthropic/claude-3.5-sonnet',
    });
  }

  async initialize(): Promise<void> {
    try {
      // Initialize ACGS client
      await this.acgsClient.initialize();
      
      // Initialize performance monitoring
      this.performanceMonitor.start();
      
      this.isInitialized = true;
      this.logger.info('OpenCode adapter initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize OpenCode adapter', error);
      throw error;
    }
  }

  async executeCommand(command: OpenCodeCommand): Promise<OpenCodeResult> {
    if (!this.isInitialized) {
      throw new Error('OpenCode adapter not initialized');
    }

    const startTime = Date.now();
    const startMemory = process.memoryUsage().heapUsed;

    try {
      // First check constitutional compliance
      const complianceResult = await this.constitutionalWrapper.checkCompliance(
        `opencode:${command.command}`,
        {
          ...command.context,
          args: command.args,
          commandLine: `opencode ${command.command} ${command.args.join(' ')}`,
        }
      );

      if (!complianceResult.compliant) {
        return {
          success: false,
          error: `Constitutional compliance failed: ${complianceResult.violations.join('; ')}`,
        };
      }

      // Then check policy through ACGS
      const policyRequest: PolicyCheckRequest = {
        action: `opencode:${command.command}`,
        resource: 'opencode-cli',
        context: {
          ...command.context,
          args: command.args,
          timestamp: new Date().toISOString(),
          constitutionalHash: complianceResult.hash,
        },
        agentId: command.context.agentId || 'opencode-adapter',
      };

      const policyResult = await this.acgsClient.checkPolicy(policyRequest);

      if (!policyResult.allowed) {
        if (policyResult.requiresHITL) {
          // Escalate to human
          const approved = await this.acgsClient.escalateToHuman(
            policyRequest.action,
            policyRequest.resource,
            policyRequest.context
          );

          if (!approved) {
            return {
              success: false,
              error: 'Human-in-the-loop rejected the operation',
            };
          }
        } else {
          return {
            success: false,
            error: policyResult.reason || 'Policy check failed',
          };
        }
      }

      // Execute AI command with governance wrapper
      const result = await this.runAICommand(command);

      // Calculate performance metrics
      const latency = Date.now() - startTime;
      const memoryUsage = process.memoryUsage().heapUsed - startMemory;

      // Record metrics
      this.performanceMonitor.recordMetric('command_latency', latency);
      this.performanceMonitor.recordMetric('memory_usage', memoryUsage);

      // Verify performance meets ACGS requirements
      if (latency > 5) {
        // 5ms P99 latency requirement
        this.logger.warn('Command exceeded latency threshold', {
          command: command.command,
          latency,
        });
      }

      return {
        success: result.success,
        output: result.output,
        error: result.error,
        performanceMetrics: {
          latency,
          memoryUsage,
        },
      };
    } catch (error) {
      this.logger.error('Failed to execute OpenCode command', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async runAICommand(command: OpenCodeCommand): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    try {
      switch (command.command) {
        case 'generate':
        case 'create':
        case 'write':
          return await this.handleCodeGeneration(command);
        
        case 'explain':
        case 'analyze':
          return await this.handleCodeExplanation(command);
        
        case 'review':
        case 'audit':
          return await this.handleCodeReview(command);
        
        case 'models':
          return await this.handleListModels();
        
        case 'chat':
        case 'ask':
          return await this.handleChatRequest(command);
        
        default:
          return {
            success: false,
            error: `Unsupported command: ${command.command}`,
          };
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  private async handleCodeGeneration(command: OpenCodeCommand): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    if (!command.prompt) {
      return {
        success: false,
        error: 'Prompt required for code generation',
      };
    }

    const codeRequest: CodeRequest = {
      prompt: command.prompt,
      language: command.language,
      model: command.model,
      context: command.context,
    };

    const response = await this.openRouterClient.generateCode(codeRequest);
    
    return {
      success: true,
      output: JSON.stringify({
        code: response.code,
        explanation: response.explanation,
        model: response.model,
        usage: response.usage,
      }, null, 2),
    };
  }

  private async handleCodeExplanation(command: OpenCodeCommand): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    const codeToExplain = command.args.join(' ') || command.context.code;
    
    if (!codeToExplain) {
      return {
        success: false,
        error: 'Code required for explanation',
      };
    }

    const explanation = await this.openRouterClient.explainCode(
      codeToExplain,
      command.language
    );
    
    return {
      success: true,
      output: explanation,
    };
  }

  private async handleCodeReview(command: OpenCodeCommand): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    const codeToReview = command.args.join(' ') || command.context.code;
    
    if (!codeToReview) {
      return {
        success: false,
        error: 'Code required for review',
      };
    }

    const review = await this.openRouterClient.reviewCode(
      codeToReview,
      command.language
    );
    
    return {
      success: true,
      output: JSON.stringify(review, null, 2),
    };
  }

  private async handleListModels(): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    const models = await this.openRouterClient.getAvailableModels();
    
    return {
      success: true,
      output: JSON.stringify(models, null, 2),
    };
  }

  private async handleChatRequest(command: OpenCodeCommand): Promise<{
    success: boolean;
    output?: string;
    error?: string;
  }> {
    if (!command.prompt) {
      return {
        success: false,
        error: 'Prompt required for chat',
      };
    }

    // Use code generation for general chat requests
    const codeRequest: CodeRequest = {
      prompt: command.prompt,
      model: command.model,
      context: command.context,
    };

    const response = await this.openRouterClient.generateCode(codeRequest);
    
    return {
      success: true,
      output: response.explanation || response.code,
    };
  }

  async shutdown(): Promise<void> {
    try {
      // Stop performance monitoring
      this.performanceMonitor.stop();

      this.isInitialized = false;
      this.logger.info('OpenRouter adapter shut down successfully');
    } catch (error) {
      this.logger.error('Error during shutdown', error);
      throw error;
    }
  }

  // Helper method to check if operation would be allowed
  async checkOperationAllowed(
    action: string,
    context: Record<string, any>
  ): Promise<boolean> {
    const policyRequest: PolicyCheckRequest = {
      action: `opencode:${action}`,
      resource: 'opencode-cli',
      context,
      agentId: context.agentId || 'opencode-adapter',
    };

    const result = await this.acgsClient.checkPolicy(policyRequest);
    return result.allowed;
  }

  // Get current performance metrics
  getPerformanceMetrics() {
    return this.performanceMonitor.getMetrics();
  }
}