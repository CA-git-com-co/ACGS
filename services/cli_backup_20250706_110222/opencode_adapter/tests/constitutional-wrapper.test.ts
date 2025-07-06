import { ConstitutionalWrapper } from '../src/constitutional-wrapper';

describe('ConstitutionalWrapper', () => {
  let wrapper: ConstitutionalWrapper;
  const testHash = 'cdd01ef066bc6cf2';

  beforeEach(() => {
    wrapper = new ConstitutionalWrapper(testHash);
  });

  describe('checkCompliance', () => {
    it('should pass compliance for safe operations', async () => {
      const result = await wrapper.checkCompliance('opencode:run', {
        args: ['test.js'],
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
      });

      expect(result.compliant).toBe(true);
      expect(result.violations).toHaveLength(0);
      expect(result.hash).toBeDefined();
      expect(result.hash).toHaveLength(64); // SHA-256 hash length
    });

    it('should fail compliance for operations without required metadata', async () => {
      const result = await wrapper.checkCompliance('opencode:run', {
        args: ['test.js'],
        // Missing agentId, requestId, timestamp
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Operational Transparency: All operations must be logged and auditable'
      );
    });

    it('should fail compliance for dangerous operations', async () => {
      const result = await wrapper.checkCompliance('rm -rf /', {
        args: ['/'],
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Safety First: Operations must not cause harm to systems or data'
      );
    });

    it('should fail compliance for operations with sensitive data', async () => {
      const result = await wrapper.checkCompliance('opencode:run', {
        args: ['--api-key=secret123'],
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
        apiKey: 'exposed-key',
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Data Privacy: Personal and sensitive data must be protected'
      );
    });

    it('should fail compliance for high-risk operations without consent', async () => {
      const result = await wrapper.checkCompliance('opencode:deploy', {
        resource: 'production-database',
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'User Consent: High-risk operations require explicit user consent'
      );
    });

    it('should pass compliance for high-risk operations with consent', async () => {
      const result = await wrapper.checkCompliance('opencode:deploy', {
        resource: 'production-database',
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
        userConsent: true,
      });

      expect(result.compliant).toBe(true);
      expect(result.violations).toHaveLength(0);
    });

    it('should fail compliance for operations exceeding resource limits', async () => {
      const result = await wrapper.checkCompliance('opencode:analyze', {
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
        estimatedMemoryMB: 2048, // Exceeds 1024MB limit
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Resource Constraints: Operations must respect system resource limits'
      );
    });

    it('should fail compliance for destructive operations without backup', async () => {
      const result = await wrapper.checkCompliance('delete-file', {
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
        hasBackup: false,
        isReversible: false,
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Operation Reversibility: Destructive operations must be reversible or have backups'
      );
    });

    it('should fail compliance for privileged operations without justification', async () => {
      const result = await wrapper.checkCompliance('sudo opencode', {
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Least Privilege: Operations must use minimum required permissions'
      );
    });
  });

  describe('getPrinciples', () => {
    it('should return all constitutional principles', () => {
      const principles = wrapper.getPrinciples();
      
      expect(principles.length).toBeGreaterThan(0);
      expect(principles.map(p => p.id)).toContain('safety');
      expect(principles.map(p => p.id)).toContain('transparency');
      expect(principles.map(p => p.id)).toContain('consent');
      expect(principles.map(p => p.id)).toContain('data-privacy');
      expect(principles.map(p => p.id)).toContain('resource-limits');
      expect(principles.map(p => p.id)).toContain('reversibility');
      expect(principles.map(p => p.id)).toContain('least-privilege');
    });
  });

  describe('addPrinciple', () => {
    it('should allow adding custom principles', async () => {
      const customPrinciple = {
        id: 'custom-test',
        name: 'Custom Test Principle',
        description: 'Test principle for unit tests',
        validator: (context: any) => context.testValue === true,
      };

      wrapper.addPrinciple(customPrinciple);
      
      const principles = wrapper.getPrinciples();
      expect(principles.map(p => p.id)).toContain('custom-test');

      // Test the custom principle works
      const result = await wrapper.checkCompliance('test', {
        agentId: 'test-agent',
        requestId: 'req-123',
        timestamp: new Date().toISOString(),
        testValue: false,
      });

      expect(result.compliant).toBe(false);
      expect(result.violations).toContain(
        'Custom Test Principle: Test principle for unit tests'
      );
    });
  });

  describe('removePrinciple', () => {
    it('should allow removing principles', () => {
      const principlesBefore = wrapper.getPrinciples().length;
      const removed = wrapper.removePrinciple('safety');
      
      expect(removed).toBe(true);
      expect(wrapper.getPrinciples().length).toBe(principlesBefore - 1);
      expect(wrapper.getPrinciples().map(p => p.id)).not.toContain('safety');
    });

    it('should return false when removing non-existent principle', () => {
      const removed = wrapper.removePrinciple('non-existent');
      expect(removed).toBe(false);
    });
  });
});