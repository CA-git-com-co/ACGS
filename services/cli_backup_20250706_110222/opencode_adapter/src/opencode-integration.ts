import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import { ACGSClient } from './acgs-client.js';
import { ACGSOpenRouterWrapper, CodeRequest, CodeResponse } from './acgs-openrouter-wrapper.js';
import { Logger } from './logger.js';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

export interface OpenCodeIntegrationConfig {
  openRouterApiKey: string;
  constitutionalHash: string;
  enableHybridMode?: boolean; // Use both OpenCode CLI and OpenRouter
  tempDirectory?: string;
  openCodeBinaryPath?: string;
}

export interface HybridRequest {
  operation: 'cli' | 'api' | 'auto';
  command?: string; // For CLI operations
  task?: 'generate' | 'review' | 'explain' | 'optimize'; // For API operations
  prompt?: string;
  code?: string;
  files?: Record<string, string>;
  language?: string;
  model?: string;
  context?: Record<string, any>;
  agentId: string;
  requestId: string;
}

export interface HybridResponse {
  success: boolean;
  source: 'opencode-cli' | 'openrouter-api' | 'hybrid';
  output?: string;
  files?: Record<string, string>;
  model?: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    estimatedCost: number;
  };
  performance: {
    latency: number;
    method: string;
  };
  error?: string;
}

export class OpenCodeIntegration extends EventEmitter {
  private acgsOpenRouterWrapper: ACGSOpenRouterWrapper;
  private logger: Logger;
  private config: Required<OpenCodeIntegrationConfig>;
  private activeProcesses: Map<string, ChildProcess> = new Map();

  constructor(acgsClient: ACGSClient, config: OpenCodeIntegrationConfig) {
    super();
    
    this.config = {
      enableHybridMode: true,
      tempDirectory: join(tmpdir(), 'acgs-opencode'),
      openCodeBinaryPath: 'opencode',
      ...config,
    };

    this.logger = new Logger('OpenCodeIntegration');
    this.acgsOpenRouterWrapper = new ACGSOpenRouterWrapper(acgsClient, {
      openRouterApiKey: config.openRouterApiKey,
      constitutionalHash: config.constitutionalHash,
    });

    this.ensureTempDirectory();
  }

  async initialize(): Promise<void> {
    try {
      await this.acgsOpenRouterWrapper.initialize();
      
      // Test OpenCode CLI availability
      if (this.config.enableHybridMode) {
        await this.testOpenCodeCLI();
      }
      
      this.logger.info('OpenCode integration initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize OpenCode integration', error);
      throw error;
    }
  }

  async processRequest(request: HybridRequest): Promise<HybridResponse> {
    const startTime = Date.now();

    try {
      // Determine processing method
      const method = this.determineProcessingMethod(request);
      
      let response: HybridResponse;

      switch (method) {
        case 'opencode-cli':
          response = await this.processWithOpenCodeCLI(request);
          break;
        case 'openrouter-api':
          response = await this.processWithOpenRouterAPI(request);
          break;
        case 'hybrid':
          response = await this.processWithHybridApproach(request);
          break;
        default:
          throw new Error(`Unknown processing method: ${method}`);
      }

      response.performance = {
        latency: Date.now() - startTime,
        method,
      };

      this.emit('request_processed', {
        requestId: request.requestId,
        method,
        latency: response.performance.latency,
        success: response.success,
      });

      return response;

    } catch (error) {
      const latency = Date.now() - startTime;
      this.logger.error('Failed to process request', error);

      return {
        success: false,
        source: 'hybrid',
        performance: { latency, method: 'error' },
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private determineProcessingMethod(request: HybridRequest): 'opencode-cli' | 'openrouter-api' | 'hybrid' {
    // Explicit operation preference
    if (request.operation === 'cli') return 'opencode-cli';
    if (request.operation === 'api') return 'openrouter-api';

    // Auto-selection logic
    if (!this.config.enableHybridMode) {
      return 'openrouter-api'; // Default to API if hybrid disabled
    }

    // Use CLI for file operations and interactive tasks
    if (request.files && Object.keys(request.files).length > 0) {
      return 'hybrid'; // Use both for complex file operations
    }

    // Use API for simple text operations
    if (request.task && ['explain', 'review'].includes(request.task)) {
      return 'openrouter-api';
    }

    // Use CLI for code generation with file output
    if (request.task === 'generate' && request.context?.outputFile) {
      return 'opencode-cli';
    }

    // Default to API for single operations
    return 'openrouter-api';
  }

  private async processWithOpenCodeCLI(request: HybridRequest): Promise<HybridResponse> {
    const workingDir = await this.prepareWorkingDirectory(request);
    
    try {
      const args = this.buildOpenCodeArgs(request);
      const result = await this.executeOpenCode(args, workingDir, request.requestId);

      // Read any output files
      const outputFiles = await this.collectOutputFiles(workingDir);

      return {
        success: result.success,
        source: 'opencode-cli',
        output: result.output,
        files: outputFiles,
        performance: { latency: 0, method: 'cli' }, // Will be set by caller
      };

    } finally {
      // Cleanup working directory
      this.cleanupWorkingDirectory(workingDir);
    }
  }

  private async processWithOpenRouterAPI(request: HybridRequest): Promise<HybridResponse> {
    if (!request.task) {
      throw new Error('Task required for OpenRouter API processing');
    }

    const codeRequest: CodeRequest = {
      task: request.task,
      prompt: request.prompt,
      code: request.code,
      language: request.language,
      model: request.model,
      context: request.context,
      agentId: request.agentId,
      requestId: request.requestId,
    };

    const apiResponse: CodeResponse = await this.acgsOpenRouterWrapper.processRequest(codeRequest);

    return {
      success: apiResponse.success,
      source: 'openrouter-api',
      output: this.formatAPIOutput(apiResponse),
      model: apiResponse.model,
      usage: apiResponse.usage,
      performance: { latency: 0, method: 'api' }, // Will be set by caller
      error: apiResponse.error,
    };
  }

  private async processWithHybridApproach(request: HybridRequest): Promise<HybridResponse> {
    // Use OpenRouter for analysis, OpenCode for file operations
    const analysisRequest: CodeRequest = {
      task: 'explain',
      prompt: request.prompt,
      code: request.code,
      language: request.language,
      model: request.model,
      context: request.context,
      agentId: request.agentId,
      requestId: `${request.requestId}-analysis`,
    };

    // Get analysis from OpenRouter
    const analysis = await this.acgsOpenRouterWrapper.processRequest(analysisRequest);
    
    // Use OpenCode CLI for file operations
    const cliRequest = {
      ...request,
      operation: 'cli' as const,
      context: {
        ...request.context,
        analysis: analysis.result?.explanation,
      },
    };

    const cliResult = await this.processWithOpenCodeCLI(cliRequest);

    return {
      success: analysis.success && cliResult.success,
      source: 'hybrid',
      output: `Analysis:\n${analysis.result?.explanation}\n\nCLI Output:\n${cliResult.output}`,
      files: cliResult.files,
      model: analysis.model,
      usage: analysis.usage,
      performance: { latency: 0, method: 'hybrid' }, // Will be set by caller
      error: analysis.error || cliResult.error,
    };
  }

  private async prepareWorkingDirectory(request: HybridRequest): Promise<string> {
    const workingDir = join(this.config.tempDirectory, request.requestId);
    
    if (!existsSync(workingDir)) {
      mkdirSync(workingDir, { recursive: true });
    }

    // Write input files
    if (request.files) {
      for (const [filename, content] of Object.entries(request.files)) {
        const filePath = join(workingDir, filename);
        writeFileSync(filePath, content, 'utf8');
      }
    }

    // Write prompt file if provided
    if (request.prompt) {
      const promptPath = join(workingDir, 'prompt.md');
      writeFileSync(promptPath, request.prompt, 'utf8');
    }

    return workingDir;
  }

  private buildOpenCodeArgs(request: HybridRequest): string[] {
    const args: string[] = [];

    if (request.command) {
      args.push(request.command);
    } else if (request.task) {
      // Map tasks to OpenCode commands
      const commandMap = {
        generate: 'generate',
        review: 'review',
        explain: 'explain',
        optimize: 'optimize',
      };
      args.push(commandMap[request.task] || 'chat');
    }

    if (request.prompt) {
      args.push('--prompt', request.prompt);
    }

    if (request.language) {
      args.push('--language', request.language);
    }

    if (request.model) {
      args.push('--model', request.model);
    }

    return args;
  }

  private async executeOpenCode(args: string[], workingDir: string, requestId: string): Promise<{
    success: boolean;
    output: string;
    error?: string;
  }> {
    return new Promise((resolve) => {
      const process = spawn(this.config.openCodeBinaryPath, args, {
        cwd: workingDir,
        env: {
          ...process.env,
          ACGS_MODE: 'true',
          ACGS_REQUEST_ID: requestId,
        },
      });

      this.activeProcesses.set(requestId, process);

      let output = '';
      let error = '';

      process.stdout.on('data', (data) => {
        output += data.toString();
      });

      process.stderr.on('data', (data) => {
        error += data.toString();
      });

      process.on('close', (code) => {
        this.activeProcesses.delete(requestId);
        
        if (code === 0) {
          resolve({ success: true, output });
        } else {
          resolve({ success: false, output, error: error || `Process exited with code ${code}` });
        }
      });

      process.on('error', (err) => {
        this.activeProcesses.delete(requestId);
        resolve({ success: false, output, error: err.message });
      });

      // Timeout after 60 seconds
      setTimeout(() => {
        if (this.activeProcesses.has(requestId)) {
          process.kill();
          this.activeProcesses.delete(requestId);
          resolve({ success: false, output, error: 'Process timeout' });
        }
      }, 60000);
    });
  }

  private async collectOutputFiles(workingDir: string): Promise<Record<string, string>> {
    const files: Record<string, string> = {};

    try {
      const fs = await import('fs/promises');
      const entries = await fs.readdir(workingDir, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isFile() && !entry.name.startsWith('.')) {
          const filePath = join(workingDir, entry.name);
          const content = readFileSync(filePath, 'utf8');
          files[entry.name] = content;
        }
      }
    } catch (error) {
      this.logger.warn('Failed to collect output files', error);
    }

    return files;
  }

  private cleanupWorkingDirectory(workingDir: string): void {
    try {
      const fs = require('fs');
      fs.rmSync(workingDir, { recursive: true, force: true });
    } catch (error) {
      this.logger.warn('Failed to cleanup working directory', error);
    }
  }

  private formatAPIOutput(response: CodeResponse): string {
    if (!response.success) {
      return response.error || 'API request failed';
    }

    const parts: string[] = [];

    if (response.result?.code) {
      parts.push(`Code:\n\`\`\`${response.result.code}\`\`\``);
    }

    if (response.result?.explanation) {
      parts.push(`Explanation:\n${response.result.explanation}`);
    }

    if (response.result?.review) {
      parts.push(`Review:\n${JSON.stringify(response.result.review, null, 2)}`);
    }

    if (response.result?.optimization) {
      parts.push(`Optimization:\n${JSON.stringify(response.result.optimization, null, 2)}`);
    }

    return parts.join('\n\n');
  }

  private async testOpenCodeCLI(): Promise<void> {
    try {
      const testProcess = spawn(this.config.openCodeBinaryPath, ['--version'], {
        timeout: 5000,
      });

      await new Promise<void>((resolve, reject) => {
        testProcess.on('close', (code) => {
          if (code === 0) {
            resolve();
          } else {
            reject(new Error(`OpenCode CLI test failed with code ${code}`));
          }
        });

        testProcess.on('error', (error) => {
          reject(error);
        });
      });

      this.logger.info('OpenCode CLI test successful');
    } catch (error) {
      this.logger.warn('OpenCode CLI not available, disabling hybrid mode', error);
      this.config.enableHybridMode = false;
    }
  }

  private ensureTempDirectory(): void {
    if (!existsSync(this.config.tempDirectory)) {
      mkdirSync(this.config.tempDirectory, { recursive: true });
    }
  }

  async getPerformanceMetrics() {
    return {
      ...(await this.acgsOpenRouterWrapper.getPerformanceMetrics()),
      activeProcesses: this.activeProcesses.size,
      hybridModeEnabled: this.config.enableHybridMode,
    };
  }

  async shutdown(): Promise<void> {
    // Kill all active processes
    for (const [requestId, process] of this.activeProcesses) {
      process.kill();
      this.logger.info('Killed active process', { requestId });
    }
    this.activeProcesses.clear();

    await this.acgsOpenRouterWrapper.shutdown();
    this.logger.info('OpenCode integration shut down');
  }
}