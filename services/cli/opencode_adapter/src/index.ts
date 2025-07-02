import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import dotenv from 'dotenv';
import { ACGSClient, ACGSConfig } from './acgs-client.js';
import { OpenCodeIntegration, HybridRequest } from './opencode-integration.js';
import { Logger } from './logger.js';

// Load environment variables
dotenv.config();

// Initialize logger
const logger = new Logger('OpenCodeAdapterService');

// Create Hono app
const app = new Hono();

// Initialize ACGS client with configuration
const acgsConfig: ACGSConfig = {
  authServiceUrl: process.env.ACGS_AUTH_SERVICE_URL || 'http://localhost:8016',
  policyServiceUrl: process.env.ACGS_POLICY_SERVICE_URL || 'http://localhost:8002',
  auditServiceUrl: process.env.ACGS_AUDIT_SERVICE_URL || 'http://localhost:8004',
  hitlServiceUrl: process.env.ACGS_HITL_SERVICE_URL || 'http://localhost:8006',
  agentId: process.env.ACGS_AGENT_ID || 'opencode-adapter',
  agentSecret: process.env.ACGS_AGENT_SECRET || '',
  constitutionalHash: process.env.ACGS_CONSTITUTIONAL_HASH || 'cdd01ef066bc6cf2',
};

const acgsClient = new ACGSClient(acgsConfig);
const openCodeIntegration = new OpenCodeIntegration(acgsClient, {
  openRouterApiKey: process.env.OPENROUTER_API_KEY || '',
  constitutionalHash: acgsConfig.constitutionalHash,
  enableHybridMode: process.env.ENABLE_HYBRID_MODE !== 'false',
  openCodeBinaryPath: process.env.OPENCODE_BINARY_PATH || 'opencode',
});

// Request validation schemas
const hybridRequestSchema = z.object({
  operation: z.enum(['cli', 'api', 'auto']).default('auto'),
  command: z.string().optional(),
  task: z.enum(['generate', 'review', 'explain', 'optimize']).optional(),
  prompt: z.string().optional(),
  code: z.string().optional(),
  files: z.record(z.string()).optional(),
  language: z.string().optional(),
  model: z.string().optional(),
  context: z.record(z.any()).default({}),
});

const checkPermissionSchema = z.object({
  action: z.string(),
  context: z.record(z.any()).default({}),
});

// Health check endpoint
app.get('/health', async (c) => {
  const metrics = await openCodeIntegration.getPerformanceMetrics();

  return c.json({
    status: 'healthy',
    version: '2.0.0',
    integration: 'OpenCode + OpenRouter',
    hybridMode: metrics.hybridModeEnabled,
    metrics: {
      ...metrics,
      timestamp: new Date().toISOString(),
    },
  });
});

// Execute hybrid OpenCode + OpenRouter request
app.post(
  '/execute',
  zValidator('json', hybridRequestSchema),
  async (c) => {
    const body = c.req.valid('json');
    
    try {
      const request: HybridRequest = {
        operation: body.operation,
        command: body.command,
        task: body.task,
        prompt: body.prompt,
        code: body.code,
        files: body.files,
        language: body.language,
        model: body.model,
        context: {
          ...body.context,
          clientIp: c.req.header('X-Forwarded-For') || c.req.header('X-Real-IP'),
        },
        agentId: body.context.agentId || 'opencode-integration',
        requestId: c.req.header('X-Request-ID') || crypto.randomUUID(),
      };

      const result = await openCodeIntegration.processRequest(request);
      
      return c.json(result);
    } catch (error) {
      logger.error('Failed to execute request', error);
      return c.json(
        {
          success: false,
          error: error instanceof Error ? error.message : 'Internal server error',
          source: 'integration-error',
          performance: { latency: 0, method: 'error' },
        },
        500
      );
    }
  }
);

// Check if an operation would be allowed
app.post(
  '/check-permission',
  zValidator('json', checkPermissionSchema),
  async (c) => {
    const body = c.req.valid('json');
    
    try {
      const allowed = await openCodeAdapter.checkOperationAllowed(
        body.action,
        body.context
      );
      
      return c.json({ allowed });
    } catch (error) {
      logger.error('Failed to check permission', error);
      return c.json(
        {
          allowed: false,
          error: error instanceof Error ? error.message : 'Internal server error',
        },
        500
      );
    }
  }
);

// Get current performance metrics
app.get('/metrics', async (c) => {
  const metrics = await openCodeIntegration.getPerformanceMetrics();
  return c.json(metrics);
});

// Get available models from OpenRouter
app.get('/models', async (c) => {
  try {
    // Access the OpenRouter provider through the integration
    const models = [
      'anthropic/claude-3.5-sonnet',
      'anthropic/claude-3-haiku',
      'openai/gpt-4o',
      'openai/gpt-4o-mini',
      'meta-llama/llama-3.1-70b-instruct',
      'google/gemini-pro-1.5',
    ]; // Simplified for demo
    
    return c.json({ models });
  } catch (error) {
    logger.error('Failed to get models', error);
    return c.json({ error: 'Failed to fetch models' }, 500);
  }
});

// Enhanced code generation endpoint
app.post('/generate', zValidator('json', z.object({
  prompt: z.string(),
  language: z.string().optional(),
  model: z.string().optional(),
  requirements: z.array(z.string()).optional(),
  context: z.record(z.any()).default({}),
})), async (c) => {
  const body = c.req.valid('json');
  
  const request: HybridRequest = {
    operation: 'api',
    task: 'generate',
    prompt: body.prompt,
    language: body.language,
    model: body.model,
    context: {
      ...body.context,
      requirements: body.requirements,
    },
    agentId: 'code-generator',
    requestId: crypto.randomUUID(),
  };

  const result = await openCodeIntegration.processRequest(request);
  return c.json(result);
});

// Code review endpoint
app.post('/review', zValidator('json', z.object({
  code: z.string(),
  language: z.string().optional(),
  model: z.string().optional(),
  focusAreas: z.array(z.string()).optional(),
})), async (c) => {
  const body = c.req.valid('json');
  
  const request: HybridRequest = {
    operation: 'api',
    task: 'review',
    code: body.code,
    language: body.language,
    model: body.model,
    context: {
      focusAreas: body.focusAreas,
    },
    agentId: 'code-reviewer',
    requestId: crypto.randomUUID(),
  };

  const result = await openCodeIntegration.processRequest(request);
  return c.json(result);
});

// Initialize and start server
async function start() {
  try {
    // Initialize OpenCode integration
    await openCodeIntegration.initialize();
    logger.info('OpenCode integration initialized successfully');

    // Start HTTP server
    const port = parseInt(process.env.PORT || '8020');
    
    serve({
      fetch: app.fetch,
      port,
    });

    logger.info(`OpenCode integration service listening on port ${port}`);

    // Handle graceful shutdown
    process.on('SIGTERM', async () => {
      logger.info('Received SIGTERM, shutting down gracefully');
      await openCodeIntegration.shutdown();
      process.exit(0);
    });

    process.on('SIGINT', async () => {
      logger.info('Received SIGINT, shutting down gracefully');
      await openCodeIntegration.shutdown();
      process.exit(0);
    });
  } catch (error) {
    logger.error('Failed to start OpenCode integration service', error);
    process.exit(1);
  }
}

// Start the service
start();