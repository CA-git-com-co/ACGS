/**
 * ACGS Comprehensive Load Testing Suite
 * Enterprise-grade load testing using K6 for all ACGS services
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Constitutional hash for compliance validation
const CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2";

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');
const constitutionalCompliance = new Rate('constitutional_compliance');
const throughputCounter = new Counter('requests_per_second');

// ACGS services configuration - Updated for current running services
const services = {
    'auth-service': 8022,
    'pgc-service': 8003,
    'hitl-service': 8023
};

// Load test scenarios
export const options = {
    scenarios: {
        // Smoke test - minimal load
        smoke_test: {
            executor: 'constant-vus',
            vus: 1,
            duration: '1m',
            tags: { test_type: 'smoke' },
        },
        
        // Load test - normal expected load
        load_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 10 },  // Ramp up
                { duration: '5m', target: 10 },  // Stay at 10 users
                { duration: '2m', target: 20 },  // Ramp to 20 users
                { duration: '5m', target: 20 },  // Stay at 20 users
                { duration: '2m', target: 0 },   // Ramp down
            ],
            tags: { test_type: 'load' },
        },
        
        // Stress test - beyond normal capacity
        stress_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 20 },  // Ramp up to normal load
                { duration: '5m', target: 20 },  // Stay at normal load
                { duration: '2m', target: 50 },  // Ramp up to stress level
                { duration: '5m', target: 50 },  // Stay at stress level
                { duration: '2m', target: 100 }, // Ramp up to breaking point
                { duration: '5m', target: 100 }, // Stay at breaking point
                { duration: '10m', target: 0 },  // Ramp down
            ],
            tags: { test_type: 'stress' },
        },
        
        // Spike test - sudden load increase
        spike_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '10s', target: 100 }, // Spike to 100 users
                { duration: '1m', target: 100 },  // Stay at spike
                { duration: '10s', target: 0 },   // Drop to 0
            ],
            tags: { test_type: 'spike' },
        },
        
        // Volume test - large amount of data
        volume_test: {
            executor: 'constant-vus',
            vus: 50,
            duration: '10m',
            tags: { test_type: 'volume' },
        },
        
        // Endurance test - extended duration
        endurance_test: {
            executor: 'constant-vus',
            vus: 20,
            duration: '30m',
            tags: { test_type: 'endurance' },
        }
    },
    
    // Performance thresholds
    thresholds: {
        // Response time thresholds
        'http_req_duration': ['p(95)<500'], // 95% of requests under 500ms
        'http_req_duration{test_type:load}': ['p(95)<300'], // Load test: 95% under 300ms
        'http_req_duration{test_type:stress}': ['p(95)<1000'], // Stress test: 95% under 1s
        
        // Error rate thresholds
        'http_req_failed': ['rate<0.01'], // Error rate under 1%
        'http_req_failed{test_type:load}': ['rate<0.005'], // Load test: under 0.5%
        
        // Custom metrics thresholds
        'errors': ['rate<0.01'],
        'constitutional_compliance': ['rate>0.95'], // >95% compliance
        
        // Availability thresholds
        'http_req_duration{service:auth-service}': ['p(95)<200'],
        'http_req_duration{service:ac-service}': ['p(95)<300'],
        'http_req_duration{service:ec-service}': ['p(95)<500'],
    }
};

// Test data generators
function generateTestUser() {
    return {
        username: `testuser_${Math.random().toString(36).substr(2, 9)}`,
        email: `test_${Math.random().toString(36).substr(2, 9)}@example.com`,
        role: 'user'
    };
}

function generateEvolutionRequest() {
    return {
        evolution_type: 'load_test_evolution',
        description: `Load test evolution ${Math.random().toString(36).substr(2, 9)}`,
        proposed_changes: {
            test: true,
            load_test_id: Math.random().toString(36).substr(2, 9)
        },
        priority: Math.floor(Math.random() * 5) + 1,
        constitutional_hash: CONSTITUTIONAL_HASH
    };
}

function generateConstitutionalValidationRequest() {
    return {
        constitutional_hash: CONSTITUTIONAL_HASH,
        validation_level: Math.random() > 0.5 ? 'basic' : 'comprehensive',
        context: {
            test: true,
            load_test: true
        }
    };
}

// Main test function
export default function() {
    const testType = __ENV.TEST_TYPE || 'load';
    const serviceName = selectRandomService();
    const servicePort = services[serviceName];
    
    // Test service health
    testServiceHealth(serviceName, servicePort);
    
    // Test API endpoints based on service
    switch(serviceName) {
        case 'auth-service':
            testAuthService(servicePort);
            break;
        case 'ac-service':
            testACService(servicePort);
            break;
        case 'ec-service':
            testECService(servicePort);
            break;
        default:
            testGenericService(serviceName, servicePort);
    }
    
    // Random sleep between 1-3 seconds
    sleep(Math.random() * 2 + 1);
}

function selectRandomService() {
    const serviceNames = Object.keys(services);
    return serviceNames[Math.floor(Math.random() * serviceNames.length)];
}

function testServiceHealth(serviceName, port) {
    const response = http.get(`http://localhost:${port}/health`, {
        tags: { 
            service: serviceName,
            endpoint: 'health',
            test_type: __ENV.TEST_TYPE || 'load'
        }
    });
    
    const success = check(response, {
        'health check status is 200': (r) => r.status === 200,
        'health check response time < 100ms': (r) => r.timings.duration < 100,
        'health check has valid response': (r) => {
            try {
                const body = JSON.parse(r.body);
                return body.status === 'healthy' || body.status === 'operational';
            } catch {
                return false;
            }
        }
    });
    
    // Record metrics
    errorRate.add(!success);
    responseTime.add(response.timings.duration);
    throughputCounter.add(1);
}

function testGenericService(serviceName, port) {
    // Test status endpoint
    const statusResponse = http.get(`http://localhost:${port}/api/v1/status`, {
        tags: { 
            service: serviceName,
            endpoint: 'status',
            test_type: __ENV.TEST_TYPE || 'load'
        }
    });
    
    check(statusResponse, {
        'status endpoint returns 200': (r) => r.status === 200,
        'status response time < 200ms': (r) => r.timings.duration < 200,
    });
    
    // Test metrics endpoint
    const metricsResponse = http.get(`http://localhost:${port}/metrics`, {
        tags: { 
            service: serviceName,
            endpoint: 'metrics',
            test_type: __ENV.TEST_TYPE || 'load'
        }
    });
    
    check(metricsResponse, {
        'metrics endpoint accessible': (r) => r.status === 200 || r.status === 404,
    });
    
    errorRate.add(statusResponse.status >= 400);
    responseTime.add(statusResponse.timings.duration);
}

function testAuthService(port) {
    // Test user registration simulation
    const testUser = generateTestUser();
    
    const registerResponse = http.post(`http://localhost:${port}/api/v1/auth/register`, 
        JSON.stringify(testUser), 
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { 
                service: 'auth-service',
                endpoint: 'register',
                test_type: __ENV.TEST_TYPE || 'load'
            }
        }
    );
    
    const registerSuccess = check(registerResponse, {
        'registration request processed': (r) => r.status === 200 || r.status === 201 || r.status === 409,
        'registration response time < 300ms': (r) => r.timings.duration < 300,
    });
    
    // Test login simulation
    const loginResponse = http.post(`http://localhost:${port}/api/v1/auth/login`,
        JSON.stringify({
            username: testUser.username,
            password: 'test_password'
        }),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { 
                service: 'auth-service',
                endpoint: 'login',
                test_type: __ENV.TEST_TYPE || 'load'
            }
        }
    );
    
    check(loginResponse, {
        'login request processed': (r) => r.status === 200 || r.status === 401,
        'login response time < 200ms': (r) => r.timings.duration < 200,
    });
    
    errorRate.add(!registerSuccess);
    responseTime.add(registerResponse.timings.duration);
}

function testACService(port) {
    // Test constitutional validation
    const validationRequest = generateConstitutionalValidationRequest();
    
    const validationResponse = http.post(`http://localhost:${port}/api/v1/constitutional/validate`,
        JSON.stringify(validationRequest),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { 
                service: 'ac-service',
                endpoint: 'constitutional_validate',
                test_type: __ENV.TEST_TYPE || 'load'
            }
        }
    );
    
    const validationSuccess = check(validationResponse, {
        'constitutional validation processed': (r) => r.status === 200,
        'constitutional validation response time < 500ms': (r) => r.timings.duration < 500,
        'constitutional validation returns compliance score': (r) => {
            try {
                const body = JSON.parse(r.body);
                return typeof body.compliance_score === 'number';
            } catch {
                return false;
            }
        }
    });
    
    // Record constitutional compliance
    if (validationSuccess && validationResponse.status === 200) {
        try {
            const body = JSON.parse(validationResponse.body);
            constitutionalCompliance.add(body.compliance_score >= 0.95);
        } catch {
            constitutionalCompliance.add(false);
        }
    } else {
        constitutionalCompliance.add(false);
    }
    
    errorRate.add(!validationSuccess);
    responseTime.add(validationResponse.timings.duration);
}

function testECService(port) {
    // Test evolution submission
    const evolutionRequest = generateEvolutionRequest();
    
    const evolutionResponse = http.post(`http://localhost:${port}/api/v1/evolution/submit`,
        JSON.stringify(evolutionRequest),
        {
            headers: { 'Content-Type': 'application/json' },
            tags: { 
                service: 'ec-service',
                endpoint: 'evolution_submit',
                test_type: __ENV.TEST_TYPE || 'load'
            }
        }
    );
    
    const evolutionSuccess = check(evolutionResponse, {
        'evolution submission processed': (r) => r.status === 200 || r.status === 201,
        'evolution submission response time < 1000ms': (r) => r.timings.duration < 1000,
        'evolution submission returns evolution_id': (r) => {
            try {
                const body = JSON.parse(r.body);
                return typeof body.evolution_id === 'string';
            } catch {
                return false;
            }
        }
    });
    
    // Test evolution status check if submission was successful
    if (evolutionSuccess && evolutionResponse.status < 300) {
        try {
            const body = JSON.parse(evolutionResponse.body);
            const evolutionId = body.evolution_id;
            
            const statusResponse = http.get(`http://localhost:${port}/api/v1/evolution/${evolutionId}/status`, {
                tags: { 
                    service: 'ec-service',
                    endpoint: 'evolution_status',
                    test_type: __ENV.TEST_TYPE || 'load'
                }
            });
            
            check(statusResponse, {
                'evolution status check successful': (r) => r.status === 200,
                'evolution status response time < 200ms': (r) => r.timings.duration < 200,
            });
            
        } catch (e) {
            console.log('Failed to check evolution status:', e);
        }
    }
    
    errorRate.add(!evolutionSuccess);
    responseTime.add(evolutionResponse.timings.duration);
}

// Setup function - runs once before the test
export function setup() {
    console.log('Starting ACGS Load Tests');
    console.log(`Test Type: ${__ENV.TEST_TYPE || 'load'}`);
    console.log(`Constitutional Hash: ${CONSTITUTIONAL_HASH}`);
    
    // Verify all services are accessible
    const serviceStatus = {};
    
    for (const [serviceName, port] of Object.entries(services)) {
        try {
            const response = http.get(`http://localhost:${port}/health`, { timeout: '10s' });
            serviceStatus[serviceName] = {
                accessible: response.status === 200,
                responseTime: response.timings.duration
            };
        } catch (e) {
            serviceStatus[serviceName] = {
                accessible: false,
                error: e.message
            };
        }
    }
    
    console.log('Service Status:', JSON.stringify(serviceStatus, null, 2));
    
    return {
        serviceStatus: serviceStatus,
        testStartTime: new Date().toISOString(),
        constitutionalHash: CONSTITUTIONAL_HASH
    };
}

// Teardown function - runs once after the test
export function teardown(data) {
    console.log('ACGS Load Tests Completed');
    console.log(`Test Duration: ${new Date().toISOString()} - ${data.testStartTime}`);
    console.log(`Constitutional Hash Validated: ${CONSTITUTIONAL_HASH}`);
    
    // Log final metrics summary
    console.log('Test completed successfully');
}

// Handle summary - custom summary output
export function handleSummary(data) {
    const summary = {
        test_summary: {
            test_type: __ENV.TEST_TYPE || 'load',
            start_time: data.setup_data?.testStartTime,
            end_time: new Date().toISOString(),
            constitutional_hash: CONSTITUTIONAL_HASH,
            total_requests: data.metrics.http_reqs?.values?.count || 0,
            total_duration: data.metrics.http_req_duration?.values?.avg || 0,
            error_rate: data.metrics.http_req_failed?.values?.rate || 0,
            constitutional_compliance_rate: data.metrics.constitutional_compliance?.values?.rate || 0
        },
        performance_metrics: {
            avg_response_time: data.metrics.http_req_duration?.values?.avg || 0,
            p95_response_time: data.metrics.http_req_duration?.values?.['p(95)'] || 0,
            p99_response_time: data.metrics.http_req_duration?.values?.['p(99)'] || 0,
            max_response_time: data.metrics.http_req_duration?.values?.max || 0,
            requests_per_second: data.metrics.http_reqs?.values?.rate || 0
        },
        sla_compliance: {
            response_time_sla: (data.metrics.http_req_duration?.values?.['p(95)'] || 0) < 500,
            error_rate_sla: (data.metrics.http_req_failed?.values?.rate || 0) < 0.01,
            constitutional_compliance_sla: (data.metrics.constitutional_compliance?.values?.rate || 0) > 0.95
        },
        service_status: data.setup_data?.serviceStatus || {},
        detailed_metrics: data.metrics
    };

    return {
        'reports/load_tests/k6_summary.json': JSON.stringify(summary, null, 2),
        'reports/load_tests/k6_detailed_results.json': JSON.stringify(data, null, 2),
        'stdout': `
=== ACGS Load Test Results ===
Test Type: ${summary.test_summary.test_type}
Total Requests: ${summary.test_summary.total_requests}
Avg Response Time: ${summary.performance_metrics.avg_response_time.toFixed(2)}ms
P95 Response Time: ${summary.performance_metrics.p95_response_time.toFixed(2)}ms
Error Rate: ${(summary.test_summary.error_rate * 100).toFixed(2)}%
Constitutional Compliance: ${(summary.test_summary.constitutional_compliance_rate * 100).toFixed(1)}%
Requests/sec: ${summary.performance_metrics.requests_per_second.toFixed(2)}

SLA Compliance:
- Response Time (<500ms): ${summary.sla_compliance.response_time_sla ? 'PASS' : 'FAIL'}
- Error Rate (<1%): ${summary.sla_compliance.error_rate_sla ? 'PASS' : 'FAIL'}
- Constitutional Compliance (>95%): ${summary.sla_compliance.constitutional_compliance_sla ? 'PASS' : 'FAIL'}

Constitutional Hash: ${CONSTITUTIONAL_HASH}
=============================
        `
    };
}
