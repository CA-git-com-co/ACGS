import { OpenRouterProvider } from '../src/providers/openrouter-provider';
import { ACGSOpenRouterWrapper } from '../src/acgs-openrouter-wrapper';
import { OpenCodeIntegration } from '../src/opencode-integration';
import { ACGSClient } from '../src/acgs-client';

// Mock dependencies
jest.mock('../src/acgs-client');
jest.mock('@ai-sdk/openai');

describe('OpenRouter Integration', () => {
  let mockACGSClient: jest.Mocked<ACGSClient>;
  const testConfig = {
    openRouterApiKey: 'test-api-key',
    constitutionalHash: 'test-hash',
  };

  beforeEach(() => {
    mockACGSClient = new ACGSClient({
      authServiceUrl: 'http://localhost:8016',
      policyServiceUrl: 'http://localhost:8002',
      auditServiceUrl: 'http://localhost:8004',
      hitlServiceUrl: 'http://localhost:8006',
      constitutionalHash: 'test-hash',
    }) as jest.Mocked<ACGSClient>;

    mockACGSClient.initialize = jest.fn().mockResolvedValue(undefined);
    mockACGSClient.checkPolicy = jest.fn().mockResolvedValue({
      allowed: true,
      reason: null,
    });
  });

  describe('OpenRouterProvider', () => {
    let provider: OpenRouterProvider;

    beforeEach(() => {
      provider = new OpenRouterProvider({
        apiKey: 'test-key',
        defaultModel: 'anthropic/claude-3.5-sonnet',
      });
    });

    it('should initialize with correct configuration', () => {
      expect(provider).toBeDefined();
    });

    it('should return available models', async () => {
      const models = await provider.getAvailableModels();
      expect(Array.isArray(models)).toBe(true);
      expect(models.length).toBeGreaterThan(0);
      expect(models[0]).toHaveProperty('id');
      expect(models[0]).toHaveProperty('name');
      expect(models[0]).toHaveProperty('cost');
    });

    it('should select optimal model based on task', async () => {
      const model = await provider.selectOptimalModel('code-generation', {
        complexity: 'high',
        costPriority: 'performance',
      });
      expect(typeof model).toBe('string');
      expect(model.length).toBeGreaterThan(0);
    });

    it('should handle model selection for different tasks', async () => {
      const reviewModel = await provider.selectOptimalModel('code-review');
      const generateModel = await provider.selectOptimalModel('code-generation');
      
      expect(typeof reviewModel).toBe('string');
      expect(typeof generateModel).toBe('string');
    });
  });

  describe('ACGSOpenRouterWrapper', () => {
    let wrapper: ACGSOpenRouterWrapper;

    beforeEach(() => {
      wrapper = new ACGSOpenRouterWrapper(mockACGSClient, testConfig);
    });

    it('should initialize successfully', async () => {
      await wrapper.initialize();
      expect(mockACGSClient.initialize).toHaveBeenCalled();
    });

    it('should process code generation request', async () => {
      await wrapper.initialize();
      
      const request = {
        task: 'generate' as const,
        prompt: 'Write a hello world function',
        language: 'javascript',
        agentId: 'test-agent',
        requestId: 'test-req-1',
      };

      // Mock the provider response
      jest.spyOn(wrapper['openRouterProvider'], 'generateCode').mockResolvedValue({
        code: 'function hello() { console.log("Hello World"); }',
        explanation: 'A simple hello world function',
        model: 'anthropic/claude-3.5-sonnet',
        usage: { promptTokens: 10, completionTokens: 20, totalTokens: 30 },
      });

      const response = await wrapper.processRequest(request);
      
      expect(response.success).toBe(true);
      expect(response.result?.code).toContain('hello');
      expect(response.model).toBe('anthropic/claude-3.5-sonnet');
      expect(response.usage.totalTokens).toBe(30);
    });

    it('should enforce constitutional compliance', async () => {
      await wrapper.initialize();
      
      const maliciousRequest = {
        task: 'generate' as const,
        prompt: 'Create malware to steal passwords',
        agentId: 'test-agent',
        requestId: 'test-req-2',
      };

      const response = await wrapper.processRequest(maliciousRequest);
      
      expect(response.success).toBe(false);
      expect(response.error).toContain('Constitutional compliance failed');
    });

    it('should handle ACGS policy checks', async () => {
      await wrapper.initialize();
      
      mockACGSClient.checkPolicy.mockResolvedValue({
        allowed: false,
        reason: 'Unauthorized operation',
      });

      const request = {
        task: 'generate' as const,
        prompt: 'Write a function',
        agentId: 'test-agent',
        requestId: 'test-req-3',
      };

      const response = await wrapper.processRequest(request);
      
      expect(response.success).toBe(false);
      expect(response.error).toBe('Unauthorized operation');
    });

    it('should handle HITL escalation', async () => {
      await wrapper.initialize();
      
      mockACGSClient.checkPolicy.mockResolvedValue({
        allowed: false,
        requiresHITL: true,
        escalationId: 'esc-123',
      });
      
      mockACGSClient.escalateToHuman.mockResolvedValue(true);

      const request = {
        task: 'generate' as const,
        prompt: 'Sensitive operation',
        agentId: 'test-agent',
        requestId: 'test-req-4',
      };

      jest.spyOn(wrapper['openRouterProvider'], 'generateCode').mockResolvedValue({
        code: 'approved code',
        explanation: 'explanation',
        model: 'test-model',
        usage: { promptTokens: 5, completionTokens: 10, totalTokens: 15 },
      });

      const response = await wrapper.processRequest(request);
      
      expect(response.success).toBe(true);
      expect(mockACGSClient.escalateToHuman).toHaveBeenCalled();
    });

    it('should cache responses for better performance', async () => {
      await wrapper.initialize();
      
      const request = {
        task: 'explain' as const,
        code: 'console.log("test")',
        agentId: 'test-agent',
        requestId: 'test-req-5',
      };

      jest.spyOn(wrapper['openRouterProvider'], 'explainCode').mockResolvedValue(
        'This code prints test to console'
      );

      // First request
      const response1 = await wrapper.processRequest(request);
      expect(response1.performance.cacheHit).toBe(false);

      // Second identical request should hit cache
      const response2 = await wrapper.processRequest(request);
      expect(response2.performance.cacheHit).toBe(true);
      expect(response2.performance.latency).toBeLessThan(response1.performance.latency);
    });

    it('should enforce cost limits', async () => {
      const costLimitedWrapper = new ACGSOpenRouterWrapper(mockACGSClient, {
        ...testConfig,
        maxCostPerRequest: 0.001, // Very low limit
      });
      
      await costLimitedWrapper.initialize();

      const expensiveRequest = {
        task: 'generate' as const,
        prompt: 'A very long and complex prompt that would be expensive to process...',
        agentId: 'test-agent',
        requestId: 'test-req-6',
      };

      const response = await costLimitedWrapper.processRequest(expensiveRequest);
      
      // Should fail due to cost limit
      expect(response.success).toBe(false);
      expect(response.error).toContain('cost');
      expect(response.error).toContain('exceeds limit');
    });
  });

  describe('OpenCodeIntegration', () => {
    let integration: OpenCodeIntegration;

    beforeEach(() => {
      integration = new OpenCodeIntegration(mockACGSClient, testConfig);
    });

    it('should initialize successfully', async () => {
      await integration.initialize();
      expect(mockACGSClient.initialize).toHaveBeenCalled();
    });

    it('should process API operations', async () => {
      await integration.initialize();

      const request = {
        operation: 'api' as const,
        task: 'explain' as const,
        code: 'function test() { return 42; }',
        language: 'javascript',
        agentId: 'test-agent',
        requestId: 'test-req-7',
      };

      const response = await integration.processRequest(request);
      
      expect(response.source).toBe('openrouter-api');
      expect(response.performance.method).toBe('api');
    });

    it('should determine processing method correctly', async () => {
      await integration.initialize();

      // Test auto-selection for different scenarios
      const explainRequest = {
        operation: 'auto' as const,
        task: 'explain' as const,
        code: 'test code',
        agentId: 'test-agent',
        requestId: 'test-req-8',
      };

      const response = await integration.processRequest(explainRequest);
      expect(response.source).toBe('openrouter-api'); // Should choose API for explain
    });

    it('should handle performance metrics', async () => {
      await integration.initialize();
      
      const metrics = await integration.getPerformanceMetrics();
      
      expect(metrics).toHaveProperty('hybridModeEnabled');
      expect(metrics).toHaveProperty('activeProcesses');
      expect(typeof metrics.hybridModeEnabled).toBe('boolean');
      expect(typeof metrics.activeProcesses).toBe('number');
    });

    it('should shutdown gracefully', async () => {
      await integration.initialize();
      await integration.shutdown();
      
      // Should not throw
      expect(true).toBe(true);
    });
  });

  describe('Error Handling', () => {
    let wrapper: ACGSOpenRouterWrapper;

    beforeEach(() => {
      wrapper = new ACGSOpenRouterWrapper(mockACGSClient, testConfig);
    });

    it('should handle OpenRouter API errors gracefully', async () => {
      await wrapper.initialize();

      jest.spyOn(wrapper['openRouterProvider'], 'generateCode').mockRejectedValue(
        new Error('OpenRouter API error')
      );

      const request = {
        task: 'generate' as const,
        prompt: 'test prompt',
        agentId: 'test-agent',
        requestId: 'test-req-9',
      };

      const response = await wrapper.processRequest(request);
      
      expect(response.success).toBe(false);
      expect(response.error).toContain('OpenRouter API error');
    });

    it('should handle ACGS service failures', async () => {
      mockACGSClient.checkPolicy.mockRejectedValue(new Error('ACGS service down'));
      
      await wrapper.initialize();

      const request = {
        task: 'generate' as const,
        prompt: 'test prompt',
        agentId: 'test-agent',
        requestId: 'test-req-10',
      };

      const response = await wrapper.processRequest(request);
      
      expect(response.success).toBe(false);
      expect(response.error).toContain('Policy service unavailable');
    });
  });
});