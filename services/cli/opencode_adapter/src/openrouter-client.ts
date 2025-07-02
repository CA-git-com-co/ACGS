import OpenAI from 'openai';
import { Logger } from './logger.js';

export interface OpenRouterConfig {
  apiKey: string;
  baseURL?: string;
  defaultModel?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface CodeRequest {
  prompt: string;
  language?: string;
  model?: string;
  context?: Record<string, any>;
}

export interface CodeResponse {
  code: string;
  explanation?: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

export class OpenRouterClient {
  private client: OpenAI;
  private logger: Logger;
  private config: OpenRouterConfig;

  constructor(config: OpenRouterConfig) {
    this.config = {
      baseURL: 'https://openrouter.ai/api/v1',
      defaultModel: 'anthropic/claude-3.5-sonnet',
      maxTokens: 4096,
      temperature: 0.1,
      ...config,
    };

    this.logger = new Logger('OpenRouterClient');

    this.client = new OpenAI({
      apiKey: this.config.apiKey,
      baseURL: this.config.baseURL,
      defaultHeaders: {
        'HTTP-Referer': 'https://acgs.ai',
        'X-Title': 'ACGS OpenCode Adapter',
      },
    });
  }

  async generateCode(request: CodeRequest): Promise<CodeResponse> {
    try {
      const model = request.model || this.config.defaultModel!;
      
      const systemPrompt = this.buildSystemPrompt(request.language, request.context);
      const userPrompt = this.buildUserPrompt(request.prompt, request.context);

      this.logger.info('Generating code with OpenRouter', {
        model,
        language: request.language,
        promptLength: request.prompt.length,
      });

      const completion = await this.client.chat.completions.create({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        max_tokens: this.config.maxTokens,
        temperature: this.config.temperature,
        stream: false,
      });

      const response = completion.choices[0]?.message?.content || '';
      
      return {
        code: this.extractCode(response),
        explanation: this.extractExplanation(response),
        model,
        usage: {
          promptTokens: completion.usage?.prompt_tokens || 0,
          completionTokens: completion.usage?.completion_tokens || 0,
          totalTokens: completion.usage?.total_tokens || 0,
        },
      };
    } catch (error) {
      this.logger.error('Failed to generate code', error);
      throw error;
    }
  }

  async reviewCode(code: string, language?: string): Promise<{
    issues: string[];
    suggestions: string[];
    securityConcerns: string[];
  }> {
    try {
      const systemPrompt = `You are an expert code reviewer. Analyze the provided code for:
1. Potential bugs and issues
2. Performance improvements
3. Security vulnerabilities
4. Best practices violations

Return your analysis in JSON format with arrays for 'issues', 'suggestions', and 'securityConcerns'.`;

      const userPrompt = `Review this ${language || 'code'}:

\`\`\`${language || ''}
${code}
\`\`\``;

      const completion = await this.client.chat.completions.create({
        model: this.config.defaultModel!,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        max_tokens: 2048,
        temperature: 0.1,
      });

      const response = completion.choices[0]?.message?.content || '{}';
      
      try {
        return JSON.parse(response);
      } catch {
        // Fallback if JSON parsing fails
        return {
          issues: [response],
          suggestions: [],
          securityConcerns: [],
        };
      }
    } catch (error) {
      this.logger.error('Failed to review code', error);
      throw error;
    }
  }

  async explainCode(code: string, language?: string): Promise<string> {
    try {
      const systemPrompt = `You are an expert programmer. Explain the provided code clearly and concisely.`;
      
      const userPrompt = `Explain this ${language || 'code'}:

\`\`\`${language || ''}
${code}
\`\`\``;

      const completion = await this.client.chat.completions.create({
        model: this.config.defaultModel!,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        max_tokens: 1024,
        temperature: 0.2,
      });

      return completion.choices[0]?.message?.content || 'Unable to explain code.';
    } catch (error) {
      this.logger.error('Failed to explain code', error);
      throw error;
    }
  }

  async getAvailableModels(): Promise<string[]> {
    try {
      // OpenRouter models endpoint
      const response = await fetch('https://openrouter.ai/api/v1/models', {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
        },
      });

      const data = await response.json();
      return data.data?.map((model: any) => model.id) || [];
    } catch (error) {
      this.logger.error('Failed to fetch models', error);
      // Return default models if API call fails
      return [
        'anthropic/claude-3.5-sonnet',
        'anthropic/claude-3-haiku',
        'openai/gpt-4o',
        'openai/gpt-4o-mini',
        'meta-llama/llama-3.1-70b-instruct',
        'google/gemini-pro-1.5',
      ];
    }
  }

  private buildSystemPrompt(language?: string, context?: Record<string, any>): string {
    let prompt = 'You are an expert software engineer and code assistant.';
    
    if (language) {
      prompt += ` You specialize in ${language} development.`;
    }

    prompt += `

IMPORTANT: You are operating under ACGS (AI Constitutional Governance System) with the following principles:
1. Safety First: Never generate harmful or malicious code
2. Security: Follow secure coding practices
3. Best Practices: Write clean, maintainable code
4. Documentation: Include comments and explanations

Always respond with properly formatted code blocks and clear explanations.`;

    if (context?.requirements) {
      prompt += `\n\nSpecific requirements: ${context.requirements}`;
    }

    return prompt;
  }

  private buildUserPrompt(prompt: string, context?: Record<string, any>): string {
    let userPrompt = prompt;

    if (context?.files) {
      userPrompt += '\n\nContext files:\n';
      for (const [filename, content] of Object.entries(context.files)) {
        userPrompt += `\n${filename}:\n\`\`\`\n${content}\n\`\`\`\n`;
      }
    }

    if (context?.constraints) {
      userPrompt += `\n\nConstraints: ${context.constraints}`;
    }

    return userPrompt;
  }

  private extractCode(response: string): string {
    // Extract code blocks from markdown
    const codeBlockRegex = /```[\w]*\n([\s\S]*?)\n```/g;
    const matches = [...response.matchAll(codeBlockRegex)];
    
    if (matches.length > 0) {
      return matches.map(match => match[1]).join('\n\n');
    }

    // If no code blocks found, return the whole response
    return response;
  }

  private extractExplanation(response: string): string {
    // Remove code blocks to get explanation text
    const withoutCodeBlocks = response.replace(/```[\s\S]*?```/g, '');
    return withoutCodeBlocks.trim();
  }
}