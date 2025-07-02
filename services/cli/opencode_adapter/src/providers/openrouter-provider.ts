import { createOpenAI } from '@ai-sdk/openai';
import { generateObject, generateText } from 'ai';
import { z } from 'zod';
import { Logger } from '../logger.js';

export interface OpenRouterConfig {
  apiKey: string;
  baseURL?: string;
  defaultModel?: string;
  maxTokens?: number;
  temperature?: number;
  enableCaching?: boolean;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  cost: {
    input: number;
    output: number;
  };
  contextLength: number;
  capabilities: {
    reasoning: boolean;
    codeGeneration: boolean;
    multimodal: boolean;
  };
}

export class OpenRouterProvider {
  private client: ReturnType<typeof createOpenAI>;
  private logger: Logger;
  private config: Required<OpenRouterConfig>;
  private modelCache: Map<string, ModelInfo> = new Map();

  constructor(config: OpenRouterConfig) {
    this.config = {
      baseURL: 'https://openrouter.ai/api/v1',
      defaultModel: 'anthropic/claude-3.5-sonnet',
      maxTokens: 4096,
      temperature: 0.1,
      enableCaching: true,
      ...config,
    };

    this.logger = new Logger('OpenRouterProvider');

    this.client = createOpenAI({
      apiKey: this.config.apiKey,
      baseURL: this.config.baseURL,
      defaultHeaders: {
        'HTTP-Referer': 'https://acgs.ai',
        'X-Title': 'ACGS OpenCode Integration',
      },
    });
  }

  async generateCode(prompt: string, options: {
    language?: string;
    model?: string;
    context?: Record<string, any>;
    requirements?: string[];
  } = {}): Promise<{
    code: string;
    explanation: string;
    model: string;
    usage: { promptTokens: number; completionTokens: number; totalTokens: number };
  }> {
    const model = options.model || this.config.defaultModel;
    const systemPrompt = this.buildSystemPrompt(options.language, options.requirements);
    const userPrompt = this.buildCodePrompt(prompt, options.context);

    try {
      this.logger.info('Generating code with OpenRouter', {
        model,
        language: options.language,
        promptLength: prompt.length,
      });

      const result = await generateText({
        model: this.client(model),
        system: systemPrompt,
        prompt: userPrompt,
        maxTokens: this.config.maxTokens,
        temperature: this.config.temperature,
      });

      const parsed = this.parseCodeResponse(result.text);

      return {
        code: parsed.code,
        explanation: parsed.explanation,
        model,
        usage: {
          promptTokens: result.usage?.promptTokens || 0,
          completionTokens: result.usage?.completionTokens || 0,
          totalTokens: result.usage?.totalTokens || 0,
        },
      };
    } catch (error) {
      this.logger.error('Failed to generate code', error);
      throw error;
    }
  }

  async reviewCode(code: string, options: {
    language?: string;
    model?: string;
    focusAreas?: string[];
  } = {}): Promise<{
    issues: Array<{ severity: 'low' | 'medium' | 'high'; message: string; line?: number }>;
    suggestions: string[];
    securityConcerns: string[];
    score: number;
  }> {
    const model = options.model || this.config.defaultModel;

    try {
      const result = await generateObject({
        model: this.client(model),
        system: `You are an expert code reviewer. Analyze code for bugs, security issues, performance problems, and best practices. 
                Focus on: ${options.focusAreas?.join(', ') || 'general code quality'}`,
        prompt: `Review this ${options.language || ''} code:\n\n\`\`\`\n${code}\n\`\`\``,
        schema: z.object({
          issues: z.array(z.object({
            severity: z.enum(['low', 'medium', 'high']),
            message: z.string(),
            line: z.number().optional(),
          })),
          suggestions: z.array(z.string()),
          securityConcerns: z.array(z.string()),
          score: z.number().min(0).max(100),
        }),
      });

      return result.object;
    } catch (error) {
      this.logger.error('Failed to review code', error);
      throw error;
    }
  }

  async explainCode(code: string, options: {
    language?: string;
    model?: string;
    detailLevel?: 'brief' | 'detailed' | 'comprehensive';
  } = {}): Promise<string> {
    const model = options.model || this.config.defaultModel;
    const detailPrompt = {
      brief: 'Provide a brief, high-level explanation.',
      detailed: 'Provide a detailed explanation with examples.',
      comprehensive: 'Provide a comprehensive explanation including edge cases and best practices.',
    }[options.detailLevel || 'detailed'];

    try {
      const result = await generateText({
        model: this.client(model),
        system: `You are an expert programmer. Explain code clearly and accurately. ${detailPrompt}`,
        prompt: `Explain this ${options.language || ''} code:\n\n\`\`\`\n${code}\n\`\`\``,
        maxTokens: 2048,
        temperature: 0.2,
      });

      return result.text;
    } catch (error) {
      this.logger.error('Failed to explain code', error);
      throw error;
    }
  }

  async optimizeCode(code: string, options: {
    language?: string;
    model?: string;
    optimizationGoals?: string[];
  } = {}): Promise<{
    optimizedCode: string;
    improvements: string[];
    performanceGains: string;
  }> {
    const model = options.model || this.config.defaultModel;
    const goals = options.optimizationGoals || ['performance', 'readability', 'maintainability'];

    try {
      const result = await generateObject({
        model: this.client(model),
        system: `You are an expert software optimizer. Improve code for: ${goals.join(', ')}`,
        prompt: `Optimize this ${options.language || ''} code:\n\n\`\`\`\n${code}\n\`\`\``,
        schema: z.object({
          optimizedCode: z.string(),
          improvements: z.array(z.string()),
          performanceGains: z.string(),
        }),
      });

      return result.object;
    } catch (error) {
      this.logger.error('Failed to optimize code', error);
      throw error;
    }
  }

  async getAvailableModels(): Promise<ModelInfo[]> {
    if (this.modelCache.size > 0 && this.config.enableCaching) {
      return Array.from(this.modelCache.values());
    }

    try {
      const response = await fetch('https://openrouter.ai/api/v1/models', {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
        },
      });

      const data = await response.json();
      const models: ModelInfo[] = data.data?.map((model: any) => ({
        id: model.id,
        name: model.name || model.id,
        provider: model.id.split('/')[0],
        cost: {
          input: parseFloat(model.pricing?.prompt || '0'),
          output: parseFloat(model.pricing?.completion || '0'),
        },
        contextLength: model.context_length || 4096,
        capabilities: {
          reasoning: model.id.includes('claude') || model.id.includes('gpt-4'),
          codeGeneration: true, // Most models support code generation
          multimodal: model.id.includes('vision') || model.id.includes('multimodal'),
        },
      })) || [];

      // Cache the models
      if (this.config.enableCaching) {
        this.modelCache.clear();
        models.forEach(model => this.modelCache.set(model.id, model));
      }

      return models;
    } catch (error) {
      this.logger.error('Failed to fetch models', error);
      // Return default models if API call fails
      return this.getDefaultModels();
    }
  }

  async selectOptimalModel(task: 'code-generation' | 'code-review' | 'explanation' | 'optimization', options: {
    complexity?: 'low' | 'medium' | 'high';
    costPriority?: 'low' | 'balanced' | 'performance';
    language?: string;
  } = {}): Promise<string> {
    const models = await this.getAvailableModels();
    
    // Model selection logic based on task and requirements
    const scoreModel = (model: ModelInfo): number => {
      let score = 0;

      // Task-specific scoring
      if (task === 'code-generation') {
        if (model.id.includes('claude')) score += 30;
        if (model.id.includes('gpt-4')) score += 25;
        if (model.capabilities.reasoning) score += 20;
      } else if (task === 'code-review') {
        if (model.id.includes('claude')) score += 35;
        if (model.capabilities.reasoning) score += 25;
      } else if (task === 'explanation') {
        if (model.id.includes('claude')) score += 30;
        if (model.id.includes('gpt')) score += 20;
      }

      // Cost priority scoring
      if (options.costPriority === 'low') {
        score += Math.max(0, 50 - (model.cost.output * 1000000)); // Prefer cheaper models
      } else if (options.costPriority === 'performance') {
        if (model.id.includes('claude-3.5-sonnet')) score += 40;
        if (model.id.includes('gpt-4o')) score += 35;
      }

      // Complexity scoring
      if (options.complexity === 'high') {
        if (model.capabilities.reasoning) score += 30;
        if (model.contextLength > 100000) score += 20;
      }

      return score;
    };

    const scoredModels = models.map(model => ({
      model,
      score: scoreModel(model),
    })).sort((a, b) => b.score - a.score);

    return scoredModels[0]?.model.id || this.config.defaultModel;
  }

  private buildSystemPrompt(language?: string, requirements?: string[]): string {
    let prompt = 'You are an expert software engineer and code assistant.';
    
    if (language) {
      prompt += ` You specialize in ${language} development.`;
    }

    prompt += `

IMPORTANT: You are operating under ACGS (AI Constitutional Governance System) with these principles:
1. Safety First: Never generate harmful, malicious, or dangerous code
2. Security: Follow secure coding practices and avoid vulnerabilities
3. Best Practices: Write clean, maintainable, well-documented code
4. Performance: Consider efficiency and optimization
5. Compliance: Ensure code meets regulatory and organizational standards

Always respond with properly formatted code blocks and clear explanations.`;

    if (requirements?.length) {
      prompt += `\n\nSpecific requirements:\n${requirements.map(r => `- ${r}`).join('\n')}`;
    }

    return prompt;
  }

  private buildCodePrompt(prompt: string, context?: Record<string, any>): string {
    let fullPrompt = prompt;

    if (context?.files) {
      fullPrompt += '\n\nContext files:\n';
      for (const [filename, content] of Object.entries(context.files)) {
        fullPrompt += `\n**${filename}:**\n\`\`\`\n${content}\n\`\`\`\n`;
      }
    }

    if (context?.constraints) {
      fullPrompt += `\n\nConstraints: ${context.constraints}`;
    }

    if (context?.examples) {
      fullPrompt += '\n\nExamples:\n' + context.examples;
    }

    return fullPrompt;
  }

  private parseCodeResponse(response: string): { code: string; explanation: string } {
    // Extract code blocks from markdown
    const codeBlockRegex = /```[\w]*\n([\s\S]*?)\n```/g;
    const matches = [...response.matchAll(codeBlockRegex)];
    
    let code = '';
    if (matches.length > 0) {
      code = matches.map(match => match[1]).join('\n\n');
    }

    // Remove code blocks to get explanation text
    const explanation = response.replace(/```[\s\S]*?```/g, '').trim();

    return { code: code || response, explanation };
  }

  private getDefaultModels(): ModelInfo[] {
    return [
      {
        id: 'anthropic/claude-3.5-sonnet',
        name: 'Claude 3.5 Sonnet',
        provider: 'anthropic',
        cost: { input: 0.000003, output: 0.000015 },
        contextLength: 200000,
        capabilities: { reasoning: true, codeGeneration: true, multimodal: false },
      },
      {
        id: 'openai/gpt-4o',
        name: 'GPT-4o',
        provider: 'openai',
        cost: { input: 0.000005, output: 0.000015 },
        contextLength: 128000,
        capabilities: { reasoning: true, codeGeneration: true, multimodal: true },
      },
      {
        id: 'anthropic/claude-3-haiku',
        name: 'Claude 3 Haiku',
        provider: 'anthropic',
        cost: { input: 0.00000025, output: 0.00000125 },
        contextLength: 200000,
        capabilities: { reasoning: false, codeGeneration: true, multimodal: false },
      },
    ];
  }
}