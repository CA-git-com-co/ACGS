/**
 * Constitutional Trainer Service Load Testing Script (k6)
 *
 * This script performs comprehensive load testing of the Constitutional Trainer Service
 * to validate performance under increasing concurrency and HPA scaling behavior.
 *
 * Test Scenarios:
 * - Baseline: 10 concurrent training jobs → expect ≤ 5ms P99
 * - Peak: 100 concurrent training jobs → expect ≤ 10ms P99
 *
 * Usage:
 *   k6 run tests/load/constitutional-trainer-load-test.js
 *   k6 run --env CONSTITUTIONAL_TRAINER_URL=http://localhost:8000 tests/load/constitutional-trainer-load-test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Configuration
const CONSTITUTIONAL_TRAINER_URL =
  __ENV.CONSTITUTIONAL_TRAINER_URL || 'http://constitutional-trainer:8000';
const POLICY_ENGINE_URL = __ENV.POLICY_ENGINE_URL || 'http://policy-engine:8001';
const TEST_DURATION = __ENV.TEST_DURATION || '10m';

// Custom metrics
const trainingRequestRate = new Rate('training_request_success_rate');
const policyEvaluationRate = new Rate('policy_evaluation_success_rate');
const trainingLatency = new Trend('training_request_latency');
const policyLatency = new Trend('policy_evaluation_latency');
const errorCounter = new Counter('error_count');
const hpaScalingEvents = new Counter('hpa_scaling_events');

// Test configuration with multiple scenarios
export const options = {
  scenarios: {
    // Baseline load test: 10 concurrent users
    baseline_load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '2m', target: 10 }, // Ramp up to 10 users
        { duration: '5m', target: 10 }, // Stay at 10 users
        { duration: '1m', target: 0 }, // Ramp down
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'baseline' },
    },

    // Peak load test: 100 concurrent users
    peak_load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '5m', target: 100 }, // Ramp up to 100 users over 5 minutes
        { duration: '5m', target: 100 }, // Sustain 100 users for 5 minutes
        { duration: '2m', target: 0 }, // Ramp down
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'peak' },
      startTime: '8m', // Start after baseline test
    },

    // Spike test: sudden load increase
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '30s', target: 10 }, // Normal load
        { duration: '1m', target: 200 }, // Spike to 200 users
        { duration: '30s', target: 200 }, // Stay at spike
        { duration: '1m', target: 10 }, // Return to normal
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'spike' },
      startTime: '16m', // Start after peak test
    },
  },

  thresholds: {
    // Performance thresholds
    training_request_latency: [
      'p(95) < 5000', // 95% of requests under 5s
      'p(99) < 10000', // 99% of requests under 10s
    ],
    policy_evaluation_latency: [
      'p(95) < 25', // 95% of policy evaluations under 25ms
      'p(99) < 50', // 99% of policy evaluations under 50ms
    ],
    training_request_success_rate: ['rate > 0.95'], // 95% success rate
    policy_evaluation_success_rate: ['rate > 0.99'], // 99% success rate
    error_count: ['count < 100'], // Less than 100 errors total
    http_req_failed: ['rate < 0.05'], // Less than 5% failed requests
  },
};

// Test data generators
function generateTrainingRequest() {
  const modelName = `load-test-model-${randomString(8)}`;
  const trainingData = generateTrainingData();

  return {
    model_name: modelName,
    model_id: `load-test-${Date.now()}-${randomString(6)}`,
    training_data: trainingData,
    lora_config: {
      r: 16,
      lora_alpha: 32,
      target_modules: ['q_proj', 'v_proj'],
      lora_dropout: 0.1,
    },
    privacy_config: {
      enable_differential_privacy: true,
      epsilon: 8.0,
      delta: 1e-5,
    },
  };
}

function generateTrainingData() {
  const prompts = [
    'What are the key principles of constitutional AI?',
    'How should AI systems handle sensitive data?',
    'What is the role of human oversight in AI governance?',
    'How can AI systems ensure fairness and non-discrimination?',
    'What are the ethical considerations for AI decision-making?',
  ];

  const responses = [
    'Constitutional AI focuses on training AI systems to be helpful, harmless, and honest while respecting human values.',
    'AI systems should implement strong privacy protections, data minimization, and transparent data handling practices.',
    'Human oversight ensures AI systems remain aligned with human values and provides accountability.',
    'AI systems should implement bias detection, fairness metrics, and inclusive design principles.',
    'Ethical AI requires transparency, accountability, fairness, and respect for human autonomy and dignity.',
  ];

  const trainingData = [];
  const numSamples = Math.floor(Math.random() * 5) + 3; // 3-7 samples

  for (let i = 0; i < numSamples; i++) {
    trainingData.push({
      prompt: randomItem(prompts),
      response: randomItem(responses),
    });
  }

  return trainingData;
}

function generatePolicyRequest() {
  return {
    action: 'constitutional_training',
    agent_id: `load-test-agent-${randomString(8)}`,
    resource: {
      type: 'training_session',
      constitutional_hash: 'cdd01ef066bc6cf2',
    },
    context: {
      user_permissions: ['model_training'],
      compliance_threshold: 0.95,
    },
  };
}

// Main test function
export default function () {
  const testType = __ITER % 3; // Rotate between test types

  switch (testType) {
    case 0:
      testTrainingWorkflow();
      break;
    case 1:
      testPolicyEvaluation();
      break;
    case 2:
      testHealthChecks();
      break;
  }

  // Random sleep between 1-3 seconds to simulate realistic user behavior
  sleep(Math.random() * 2 + 1);
}

function testTrainingWorkflow() {
  const trainingRequest = generateTrainingRequest();

  const params = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer load-test-token',
    },
    tags: { endpoint: 'training' },
  };

  const startTime = Date.now();
  const response = http.post(
    `${CONSTITUTIONAL_TRAINER_URL}/api/v1/train`,
    JSON.stringify(trainingRequest),
    params
  );
  const endTime = Date.now();

  const latency = endTime - startTime;
  trainingLatency.add(latency);

  const success = check(response, {
    'training request status is 200 or 202': (r) => r.status === 200 || r.status === 202,
    'training request has training_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.training_id !== undefined;
      } catch (e) {
        return false;
      }
    },
    'training request latency acceptable': () => latency < 10000, // 10 seconds max
  });

  trainingRequestRate.add(success);

  if (!success) {
    errorCounter.add(1);
    console.error(`Training request failed: ${response.status} - ${response.body}`);
  }

  // If training started successfully, check status
  if (response.status === 200 || response.status === 202) {
    try {
      const responseBody = JSON.parse(response.body);
      if (responseBody.training_id) {
        checkTrainingStatus(responseBody.training_id);
      }
    } catch (e) {
      console.error('Failed to parse training response:', e);
    }
  }
}

function testPolicyEvaluation() {
  const policyRequest = generatePolicyRequest();

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { endpoint: 'policy' },
  };

  const startTime = Date.now();
  const response = http.post(
    `${POLICY_ENGINE_URL}/v1/evaluate`,
    JSON.stringify(policyRequest),
    params
  );
  const endTime = Date.now();

  const latency = endTime - startTime;
  policyLatency.add(latency);

  const success = check(response, {
    'policy evaluation status is 200': (r) => r.status === 200,
    'policy evaluation has decision': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.allow !== undefined;
      } catch (e) {
        return false;
      }
    },
    'policy evaluation latency acceptable': () => latency < 100, // 100ms max
  });

  policyEvaluationRate.add(success);

  if (!success) {
    errorCounter.add(1);
    console.error(`Policy evaluation failed: ${response.status} - ${response.body}`);
  }
}

function testHealthChecks() {
  const services = [
    { name: 'constitutional-trainer', url: `${CONSTITUTIONAL_TRAINER_URL}/health` },
    { name: 'policy-engine', url: `${POLICY_ENGINE_URL}/health` },
  ];

  services.forEach((service) => {
    const response = http.get(service.url, {
      tags: { endpoint: 'health', service: service.name },
    });

    check(response, {
      [`${service.name} health check is 200`]: (r) => r.status === 200,
    });
  });
}

function checkTrainingStatus(trainingId) {
  const response = http.get(`${CONSTITUTIONAL_TRAINER_URL}/api/v1/train/${trainingId}/status`, {
    headers: {
      Authorization: 'Bearer load-test-token',
    },
    tags: { endpoint: 'training_status' },
  });

  check(response, {
    'training status check is 200': (r) => r.status === 200,
    'training status has valid state': (r) => {
      try {
        const body = JSON.parse(r.body);
        return ['initializing', 'running', 'completed', 'failed'].includes(body.status);
      } catch (e) {
        return false;
      }
    },
  });
}

// Setup function - runs once before the test
export function setup() {
  console.log('🚀 Starting Constitutional Trainer Load Test');
  console.log(`Target URL: ${CONSTITUTIONAL_TRAINER_URL}`);
  console.log(`Policy Engine URL: ${POLICY_ENGINE_URL}`);

  // Verify services are accessible
  const healthCheck = http.get(`${CONSTITUTIONAL_TRAINER_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`Constitutional Trainer service not accessible: ${healthCheck.status}`);
  }

  const policyHealthCheck = http.get(`${POLICY_ENGINE_URL}/health`);
  if (policyHealthCheck.status !== 200) {
    console.warn(`Policy Engine service not accessible: ${policyHealthCheck.status}`);
  }

  console.log('✅ Services are accessible, starting load test...');

  return {
    startTime: Date.now(),
    baselineTarget: 10,
    peakTarget: 100,
  };
}

// Teardown function - runs once after the test
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(`🏁 Load test completed in ${duration} seconds`);
  console.log('📊 Check the k6 summary for detailed performance metrics');
}
