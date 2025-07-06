import { OpenCodeAdapter } from '../src/opencode-adapter';
import { ACGSClient } from '../src/acgs-client';

// Mock child_process
jest.mock('child_process', () => ({
  spawn: jest.fn(() => ({
    stdout: { on: jest.fn() },
    stderr: { on: jest.fn() },
    on: jest.fn((event, callback) => {
      if (event === 'close') {
        setTimeout(() => callback(0), 10);
      }
    }),
    kill: jest.fn(),
  })),
}));

// Mock ACGSClient
jest.mock('../src/acgs-client');

describe('OpenCodeAdapter', () => {
  let adapter: OpenCodeAdapter;
  let mockACGSClient: jest.Mocked<ACGSClient>;
  const testHash = 'cdd01ef066bc6cf2';

  beforeEach(() => {
    mockACGSClient = new ACGSClient({
      authServiceUrl: 'http://localhost:8016',
      policyServiceUrl: 'http://localhost:8002',
      auditServiceUrl: 'http://localhost:8004',
      hitlServiceUrl: 'http://localhost:8006',
      constitutionalHash: testHash,
    }) as jest.Mocked<ACGSClient>;

    mockACGSClient.initialize = jest.fn().mockResolvedValue(undefined);
    mockACGSClient.checkPolicy = jest.fn().mockResolvedValue({
      allowed: true,
      reason: null,
    });
    mockACGSClient.escalateToHuman = jest.fn().mockResolvedValue(true);

    adapter = new OpenCodeAdapter(mockACGSClient, testHash);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('initialize', () => {
    it('should initialize successfully', async () => {
      await adapter.initialize();
      expect(mockACGSClient.initialize).toHaveBeenCalled();
    });

    it('should throw error if ACGS client initialization fails', async () => {
      mockACGSClient.initialize.mockRejectedValue(new Error('Auth failed'));
      
      await expect(adapter.initialize()).rejects.toThrow('Auth failed');
    });
  });

  describe('executeCommand', () => {
    beforeEach(async () => {
      await adapter.initialize();
    });

    it('should execute allowed commands successfully', async () => {
      const command = {
        command: 'run',
        args: ['test.js'],
        context: {
          agentId: 'test-agent',
          requestId: 'req-123',
          timestamp: new Date().toISOString(),
        },
      };

      const result = await adapter.executeCommand(command);

      expect(result.success).toBe(true);
      expect(result.performanceMetrics).toBeDefined();
      expect(result.performanceMetrics?.latency).toBeGreaterThan(0);
      expect(mockACGSClient.checkPolicy).toHaveBeenCalled();
    });

    it('should fail when not initialized', async () => {
      const uninitializedAdapter = new OpenCodeAdapter(mockACGSClient, testHash);
      
      const command = {
        command: 'run',
        args: ['test.js'],
        context: {},
      };

      await expect(uninitializedAdapter.executeCommand(command)).rejects.toThrow(
        'OpenCode adapter not initialized'
      );
    });

    it('should fail constitutional compliance for dangerous operations', async () => {
      const command = {
        command: 'exec',
        args: ['rm', '-rf', '/'],
        context: {
          agentId: 'test-agent',
          requestId: 'req-123',
          timestamp: new Date().toISOString(),
          operation: 'rm -rf /',
        },
      };

      const result = await adapter.executeCommand(command);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Constitutional compliance failed');
      expect(mockACGSClient.checkPolicy).not.toHaveBeenCalled();
    });

    it('should handle policy denial', async () => {
      mockACGSClient.checkPolicy.mockResolvedValue({
        allowed: false,
        reason: 'Policy violation: unauthorized action',
      });

      const command = {
        command: 'deploy',
        args: ['production'],
        context: {
          agentId: 'test-agent',
          requestId: 'req-123',
          timestamp: new Date().toISOString(),
        },
      };

      const result = await adapter.executeCommand(command);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Policy violation: unauthorized action');
    });

    it('should handle HITL escalation approval', async () => {
      mockACGSClient.checkPolicy.mockResolvedValue({
        allowed: false,
        requiresHITL: true,
        escalationId: 'esc-123',
      });
      mockACGSClient.escalateToHuman.mockResolvedValue(true);

      const command = {
        command: 'sensitive-operation',
        args: [],
        context: {
          agentId: 'test-agent',
          requestId: 'req-123',
          timestamp: new Date().toISOString(),
        },
      };

      const result = await adapter.executeCommand(command);

      expect(result.success).toBe(true);
      expect(mockACGSClient.escalateToHuman).toHaveBeenCalled();
    });

    it('should handle HITL escalation rejection', async () => {
      mockACGSClient.checkPolicy.mockResolvedValue({
        allowed: false,
        requiresHITL: true,
        escalationId: 'esc-123',
      });
      mockACGSClient.escalateToHuman.mockResolvedValue(false);

      const command = {
        command: 'sensitive-operation',
        args: [],
        context: {
          agentId: 'test-agent',
          requestId: 'req-123',
          timestamp: new Date().toISOString(),
        },
      };

      const result = await adapter.executeCommand(command);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Human-in-the-loop rejected the operation');
    });
  });

  describe('checkOperationAllowed', () => {
    beforeEach(async () => {
      await adapter.initialize();
    });

    it('should return true for allowed operations', async () => {
      const allowed = await adapter.checkOperationAllowed('read-file', {
        agentId: 'test-agent',
      });

      expect(allowed).toBe(true);
      expect(mockACGSClient.checkPolicy).toHaveBeenCalled();
    });

    it('should return false for denied operations', async () => {
      mockACGSClient.checkPolicy.mockResolvedValue({
        allowed: false,
        reason: 'Insufficient permissions',
      });

      const allowed = await adapter.checkOperationAllowed('delete-database', {
        agentId: 'test-agent',
      });

      expect(allowed).toBe(false);
    });
  });

  describe('getPerformanceMetrics', () => {
    it('should return performance metrics', async () => {
      await adapter.initialize();
      
      // Execute a command to generate metrics
      await adapter.executeCommand({
        command: 'test',
        args: [],
        context: {
          agentId: 'test-agent',
          requestId: 'req-123',
          timestamp: new Date().toISOString(),
        },
      });

      const metrics = adapter.getPerformanceMetrics();
      expect(metrics).toBeDefined();
      expect(metrics.command_latency).toBeDefined();
    });
  });

  describe('shutdown', () => {
    it('should shutdown gracefully', async () => {
      await adapter.initialize();
      await adapter.shutdown();
      
      // Should not throw
      expect(true).toBe(true);
    });
  });
});