# ACGS-1 Project Commands and Guidelines

This document provides standardized commands and coding guidelines for the ACGS-1 Constitutional Governance System project. All team members must follow these standards to ensure code quality and consistency.

## Table of Contents
- [Build/Test/Lint Commands](#buildtestlint-commands)
- [Docker and Deployment Commands](#docker-and-deployment-commands)
- [Code Quality Guidelines](#code-quality-guidelines)
- [Architecture Design Principles](#architecture-design-principles)
- [Naming Conventions](#naming-conventions)
- [Error Handling](#error-handling)
- [Security Best Practices](#security-best-practices)
- [Performance Optimization](#performance-optimization)
- [Documentation Standards](#documentation-standards)
- [CI/CD and Workflow](#cicd-and-workflow)
- [Infrastructure Management](#infrastructure-management)
- [Monitoring and Observability](#monitoring-and-observability)

## Build/Test/Lint Commands

### Python Testing
```bash
# Run all Python tests with verbose output and stop on first failure
pytest -xvs tests/

# Run a specific test function within a file
pytest -xvs tests/test_specific_file.py::test_function

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run tests in parallel (4 workers)
pytest -xvs tests/ -n 4

# Run tests with HTML report
pytest tests/ --html=reports/report.html --self-contained-html
```

### JavaScript Testing
```bash
# Run all JavaScript/TypeScript tests
npm test

# Run only council hook-related tests
npm run test:hooks

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- path/to/test.test.ts
```

### Blockchain Testing
```bash
# Run Solana/Anchor tests with extended timeout (16.7 minutes)
cd blockchain && yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/specific_test.ts

# Run all Anchor tests
cd blockchain && anchor test

# Run specific Anchor test
cd blockchain && anchor test --skip-build --skip-deploy tests/specific_test.ts

# Run with local validator
cd blockchain && anchor test --skip-local-validator=false
```

### Linting & Type Checking
```bash
# Python linting
ruff check .

# Python auto-fix formatting issues
ruff check . --fix

# Python type checking
mypy .

# TypeScript type checking
npm run typecheck

# TypeScript and JavaScript linting
npm run lint

# Fix TypeScript and JavaScript linting issues
npm run lint:fix

# Solana/Anchor linting
cd blockchain && anchor lint
```

### Automated Code Formatting
```bash
# Format Python code with Black
black .

# Format TypeScript/JavaScript with Prettier
npm run format

# Format Rust code with rustfmt
cd blockchain && cargo fmt
```

## Docker and Deployment Commands

### Docker Environment
```bash
# Build and start the Docker development environment
docker-compose up -d

# Build and start specific services
docker-compose up -d pgc_service ac_service

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f pgc_service

# Rebuild services after changes
docker-compose up -d --build

# Stop all services
docker-compose down
```

### Kubernetes Deployment
```bash
# Deploy services to Kubernetes
kubectl apply -f infrastructure/kubernetes/deployment.yaml

# Deploy specific service
kubectl apply -f infrastructure/kubernetes/pgc-service.yaml

# View service logs
kubectl logs -f deployment/pgc-service

# Port forward for local development
kubectl port-forward service/pgc-service 8005:8005

# View all deployments
kubectl get deployments
```

### Environment Configuration
```bash
# Set up local development environment
./scripts/setup/quick_start.sh

# Generate production configuration
./scripts/setup/setup_production_complete.py

# Set up monitoring and alerting
./scripts/setup/setup_monitoring_alerting.py

# Set up backup and disaster recovery
./scripts/setup/setup_backup_disaster_recovery.py
```

### Blockchain Deployment
```bash
# Deploy and initialize the constitutional governance smart contracts
cd blockchain && yarn run initialize-constitution

# Deploy to devnet
cd blockchain && ./scripts/deploy_to_devnet.sh

# Verify deployment status
cd blockchain && ./scripts/deployment_status.sh
```

### CI/CD Validation
```bash
# Execute the complete CI/CD test suite
./scripts/ci_cd_test.sh

# Validate enterprise CI pipeline
./scripts/enterprise/validate-enterprise-ci.sh

# Run 24-point validation checks
./scripts/validate-24-checks.sh
```

## Code Quality Guidelines

### Python
- **Type Annotations**: Use typing module for all functions and variables
  ```python
  def validate_compliance(action: str, context: dict[str, Any]) -> ComplianceResult:
      # Implementation
  ```
- **Docstrings**: Follow Google style with params, returns, raises
  ```python
  def validate_compliance(action: str, context: dict[str, Any]) -> ComplianceResult:
      """Validates if an action complies with governance policies.

      Args:
          action: The action string to validate
          context: Context dictionary with governance state

      Returns:
          ComplianceResult object with validation status

      Raises:
          ValidationError: If input data is malformed
          ServiceUnavailableError: If dependent service is down
      """
  ```
- **Code Structure**:
  - Max line length: 88 characters (Black formatter)
  - Maximum function length: 50 lines
  - Maximum class length: 300 lines
  - Use dataclasses for data containers
  
- **Async Code**:
  - Prefer async/await pattern for all I/O operations
  - Use proper cancellation patterns with asyncio.CancelledError
  - Implement proper timeout handling
  - Use asyncio.gather for parallel operations with error handling
  
- **Imports**:
  - Group imports: standard library, third-party, local
  - Use absolute imports for clarity
  - Use specific imports rather than wildcard imports

### TypeScript/JavaScript
- **Typing**: Use comprehensive interfaces with JSDoc comments
  ```typescript
  /**
   * Represents a constitutional principle in the governance system
   */
  interface Principle {
    /** Unique identifier for the principle */
    id: string;
    /** Human-readable title */
    title: string;
    /** Full description of the principle */
    content: string;
    /** Category for organization */
    category: PrincipleCategory;
    /** Priority level (1-10) */
    priority: number;
  }
  ```
- **Component Structure**:
  - Separate business logic from UI components
  - Use custom hooks for reusable logic
  - Keep components under 150 lines
  - Implement proper prop validation with Zod
  - Use functional components with React hooks

- **Performance**:
  - Memoize expensive calculations with useMemo
  - Use useCallback for event handlers passed as props
  - Implement code splitting for large component trees
  - Use React.memo for pure components that render often
  - Virtualize long lists with react-window or similar libraries

- **State Management**:
  - Use React Context for global shared state
  - Implement proper reducer pattern for complex state
  - Use immutable state updates
  - Consider using Zustand for complex state management
  - Avoid prop drilling with composition

### Rust/Solana
- **Safety**:
  - Enable overflow checks in all environments
  - Use proper error types and propagation
  - Never use unsafe code without review
  - Use Clippy with strict linting rules
  - Implement comprehensive input validation

- **Documentation**:
  - Document all public functions with rustdoc
  - Include security considerations in comments
  - Explain complex algorithms with diagrams/comments
  - Add examples to all public API functions
  - Document invariants and pre/post conditions

- **Testing**:
  - 100% test coverage for critical contract functions
  - Include property-based testing for mathematical operations
  - Test all error conditions explicitly
  - Implement fuzz testing for critical functions
  - Use test fixtures for complex test scenarios

- **Performance**:
  - Minimize heap allocations in hot paths
  - Use Borsh for efficient serialization/deserialization
  - Implement proper batching for multiple operations
  - Use parallelism where appropriate
  - Profile and optimize critical paths

## Architecture Design Principles

### Service Design
- **Bounded Contexts**: 
  - Define clear service boundaries
  - Maintain independent deployability
  - Implement proper versioning for APIs
  - Design for fault isolation
  - Document interface contracts

- **Communication Patterns**:
  - Use REST for synchronous request/response
  - Use gRPC for high-performance internal services
  - Implement proper retry policies with backoff
  - Design for eventual consistency where appropriate
  - Document failure modes and recovery strategies

- **Database Design**:
  - Normalize database schemas to appropriate level
  - Implement proper indexing strategies
  - Use connection pooling
  - Implement proper database migrations
  - Document entity relationships

### Microservice Patterns
- **Circuit Breaker**:
  - Implement for all external service calls
  - Configure proper thresholds and timeouts
  - Implement fallback strategies
  - Monitor and alert on circuit state changes
  - Test circuit breaker behavior

- **Service Discovery**:
  - Use Kubernetes service discovery when available
  - Implement proper health checks
  - Configure proper DNS resolution
  - Document service dependencies
  - Test service discovery during chaos conditions

- **API Gateway**:
  - Implement rate limiting
  - Configure proper request validation
  - Implement authentication/authorization
  - Monitor API usage patterns
  - Document API endpoints

## Naming Conventions

- **Files**:
  - React components: `ComponentName.tsx` (PascalCase)
  - Hooks: `useHookName.ts` (camelCase)
  - Utilities: `utilityName.ts` (camelCase)
  - Python modules: `module_name.py` (snake_case)
  - Rust files: `module_name.rs` (snake_case)
  - Configuration files: `service-name.config.ts` (kebab-case)
  - Test files: `module_name.test.ts` or `test_module_name.py`

- **Variables**:
  - Regular variables: `camelCase` (JS/TS), `snake_case` (Python/Rust)
  - Constants: `SCREAMING_SNAKE_CASE`
  - Private class members: `_camelCaseWithUnderscore` (JS/TS), `_snake_case` (Python)
  - Boolean variables: Use prefix like `is_`, `has_`, `should_`
  - Enums: PascalCase for name, SCREAMING_SNAKE_CASE for values

- **Functions/Methods**:
  - Use verb phrases describing actions
  - Examples: `validatePolicy()`, `getPrincipleById()`, `calculateComplianceScore()`
  - Async functions: prefix with `async` or suffix with `Async` in JS/TS
  - Event handlers: prefix with `handle` or `on` (e.g., `handleSubmit`, `onUserClick`)
  - Getters/setters: prefix with `get`/`set` in JS/TS

- **Types/Interfaces**:
  - Use PascalCase with descriptive names
  - Examples: `ConstitutionalPrinciple`, `GovernanceState`
  - Avoid generic names like `Manager`, `Processor`, `Handler`
  - Interface names should not start with "I" prefix
  - Use consistent suffix for similar types (e.g., `xxxProps`, `xxxState`)

- **Test Files**:
  - Python: `test_module_name.py`
  - TypeScript/JavaScript: `module_name.test.ts`
  - Group tests logically by feature/function
  - Test fixtures: `conftest.py` for pytest
  - Mock data: `xxx.mock.ts` or `mock_xxx.py`

- **Database**:
  - Tables: snake_case, plural (e.g., `governance_principles`)
  - Columns: snake_case
  - Primary keys: `id` or `xxx_id`
  - Foreign keys: `xxx_id` (e.g., `principle_id`)
  - Join tables: combine both table names (e.g., `principles_categories`)

## Error Handling

- **Python**:
  - Use structured logging with detailed context
  - Implement custom exception hierarchy
  ```python
  class ACGSError(Exception):
      """Base exception for all ACGS errors."""
      
  class ValidationError(ACGSError):
      """Raised when input validation fails."""
      
  class ServiceUnavailableError(ACGSError):
      """Raised when a required service is unavailable."""
  ```
  - Include traceability information in logs
  - Always clean up resources in finally blocks
  - Use context managers for resource handling
  - Handle specific exceptions, not broad except blocks
  - Implement proper error classification (user error vs. system error)

- **TypeScript**:
  - Implement service-specific error boundaries
  - Use proper loading states with timeouts
  - Include error recovery mechanisms
  - Provide helpful error messages to users
  - Log detailed error information for debugging
  - Use typed error handling with discriminated unions
  - Implement proper error propagation patterns
  - Use async/await with try/catch for async code
  - Provide fallback UI for error states

- **Solana**:
  - Define explicit error enum for all possible failure modes
  - Include descriptive error messages
  - Implement transaction retry logic for network issues
  - Validate all inputs before processing
  - Use proper error propagation with `?` operator
  - Implement comprehensive error logging
  - Handle account validation errors explicitly
  - Implement proper transaction simulation before submission
  - Document all error cases in public interfaces

- **HTTP API Errors**:
  - Use proper HTTP status codes
  - Implement consistent error response format
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input data",
      "details": [...],
      "traceId": "abc123"
    }
  }
  ```
  - Include correlation IDs for tracking
  - Document error responses in API documentation
  - Implement proper validation error formatting
  - Avoid exposing internal errors to clients

## Security Best Practices

- **Input Validation**:
  - Validate all inputs at service boundaries
  - Use strict schemas for data validation
  - Sanitize user-provided data before use
  - Implement proper input size limits
  - Validate data types and formats
  - Use parameterized queries for database access
  - Implement proper content type validation

- **Authentication/Authorization**:
  - Implement proper role-based access control
  - Use short-lived JWT tokens
  - Validate permissions for all governance actions
  - Implement proper token refresh mechanisms
  - Use secure cookie settings (HttpOnly, Secure, SameSite)
  - Implement proper session management
  - Use multi-factor authentication where appropriate
  - Implement proper rate limiting for authentication endpoints

- **Smart Contract Security**:
  - Follow Anchor security best practices
  - Implement comprehensive ownership checks
  - Never use raw lamport transfers without validation
  - Validate all account types and owners
  - Implement proper reentrancy protection
  - Use proper program derived addresses (PDAs)
  - Implement comprehensive access control
  - Validate all mathematical operations against overflow/underflow
  - Document security assumptions in comments

- **API Security**:
  - Use HTTPS for all communications
  - Implement rate limiting
  - Add CSRF protection for web endpoints
  - Use proper CORS configuration
  - Implement content security policy
  - Use security headers (X-Content-Type-Options, X-Frame-Options)
  - Implement proper API key management
  - Document security requirements in API documentation

- **Data Protection**:
  - Encrypt sensitive data at rest
  - Implement proper key management
  - Use TLS 1.3 for data in transit
  - Implement proper data classification
  - Use secure deletion when appropriate
  - Implement proper backup encryption
  - Document data protection measures

## Performance Optimization

### Backend Performance
- **Database Optimization**:
  - Index critical query paths
  - Use query optimization techniques
  - Implement proper connection pooling
  - Use database-specific optimization features
  - Regularly analyze and optimize slow queries
  - Implement proper pagination for large result sets
  - Use appropriate isolation levels

- **Caching Strategy**:
  - Implement Redis caching for frequently accessed data
  - Use proper cache invalidation strategies
  - Implement distributed caching for horizontal scaling
  - Document cache dependencies and lifetimes
  - Monitor cache hit rates
  - Implement proper error handling for cache failures

- **Asynchronous Processing**:
  - Use message queues for background processing
  - Implement proper retry mechanisms
  - Use idempotent operations for reliability
  - Document message formats and schemas
  - Implement proper dead letter queues
  - Monitor queue depths and processing times

### Frontend Performance
- **Rendering Optimization**:
  - Implement code splitting
  - Use proper memoization techniques
  - Minimize DOM manipulations
  - Optimize component re-renders
  - Use virtualization for large lists
  - Implement proper lazy loading
  - Monitor component render times

- **Network Optimization**:
  - Minimize bundle sizes
  - Implement proper caching strategies
  - Use HTTP/2 or HTTP/3 when available
  - Implement proper compression
  - Use CDN for static assets
  - Implement proper retry strategies for unreliable networks
  - Monitor network request times

- **Resource Loading**:
  - Optimize critical rendering path
  - Implement proper preloading
  - Use responsive images
  - Implement proper resource hints (preconnect, prefetch)
  - Monitor resource loading times
  - Implement proper loading indicators

## Documentation Standards

### API Documentation
- Use OpenAPI/Swagger for REST APIs
- Document all endpoints, parameters, and responses
- Include authentication requirements
- Document error responses
- Include examples for complex requests/responses
- Provide versioning information

### Code Documentation
- Use JSDoc for JavaScript/TypeScript
- Use docstrings for Python
- Use rustdoc for Rust
- Document function parameters and return values
- Include usage examples for complex functions
- Document side effects and assumptions
- Reference architecture documents where appropriate

### Architecture Documentation
- Maintain high-level architecture diagrams
- Document service interactions
- Include data flow diagrams
- Document technology choices and trade-offs
- Include performance characteristics
- Document security considerations
- Update documentation when architecture changes

### User Documentation
- Maintain comprehensive user guides
- Include screenshots and step-by-step instructions
- Document all features and configurations
- Include troubleshooting information
- Use clear, concise language
- Update documentation when features change

## CI/CD and Workflow

### CI/CD Pipeline
- **Pull Request Validation**:
  - Run linting checks
  - Run unit tests
  - Run integration tests
  - Verify code coverage
  - Perform security scanning
  - Verify documentation updates

- **Deployment Pipeline**:
  - Build artifacts
  - Run acceptance tests
  - Deploy to staging environment
  - Run smoke tests
  - Deploy to production
  - Verify deployment
  - Run post-deployment verification

- **Monitoring**:
  - Monitor deployment health
  - Track performance metrics
  - Alert on anomalies
  - Implement proper rollback procedures
  - Document incident response procedures

### Version Control
- **Branch Strategy**:
  - Use feature branches for development
  - Use pull requests for code review
  - Implement proper branch protection
  - Use semantic versioning
  - Document release notes
  - Implement proper tagging strategy

- **Commit Messages**:
  - Use conventional commits format
  - Include issue references
  - Be descriptive but concise
  - Include rationale for complex changes
  - Document breaking changes

- **Code Reviews**:
  - Verify code quality
  - Verify test coverage
  - Verify documentation updates
  - Verify security considerations
  - Provide constructive feedback

## Infrastructure Management

### Kubernetes
- **Resource Management**:
  - Define appropriate resource requests and limits
  - Implement proper auto-scaling
  - Use node affinity for specialized workloads
  - Implement proper liveness and readiness probes
  - Document resource requirements

- **Configuration**:
  - Use ConfigMaps for configuration
  - Use Secrets for sensitive data
  - Implement proper environment-specific configuration
  - Document configuration options
  - Implement proper validation for configuration

- **Networking**:
  - Use Services for internal communication
  - Use Ingress for external access
  - Implement proper network policies
  - Use service mesh for complex routing
  - Document network architecture

### Docker
- **Image Building**:
  - Use multi-stage builds
  - Minimize image size
  - Use proper base images
  - Implement proper caching strategies
  - Document build process

- **Container Security**:
  - Run containers as non-root
  - Use read-only file systems where possible
  - Implement proper security scanning
  - Use minimal base images
  - Document security considerations

- **Resource Management**:
  - Define appropriate resource limits
  - Implement proper health checks
  - Use proper logging configuration
  - Document resource requirements

## Monitoring and Observability

### Metrics
- **Service Metrics**:
  - Track request rates
  - Monitor error rates
  - Track latency percentiles (p50, p95, p99)
  - Monitor resource utilization
  - Track business metrics
  - Document metric significance

- **Infrastructure Metrics**:
  - Monitor CPU and memory usage
  - Track disk I/O
  - Monitor network traffic
  - Track database performance
  - Document alert thresholds

- **User Experience Metrics**:
  - Track page load times
  - Monitor client-side errors
  - Track user interactions
  - Monitor conversion rates
  - Document user experience goals

### Logging
- **Log Format**:
  - Use structured logging
  - Include correlation IDs
  - Log appropriate level of detail
  - Include timestamp and service information
  - Document log format

- **Log Management**:
  - Implement proper log aggregation
  - Define appropriate retention policies
  - Implement proper log search
  - Use proper log sampling for high-volume services
  - Document log management procedures

### Alerting
- **Alert Design**:
  - Define appropriate alert thresholds
  - Implement proper alert routing
  - Use proper alert severity levels
  - Implement alert aggregation
  - Document alert response procedures

- **On-Call Procedures**:
  - Define escalation procedures
  - Document incident response
  - Implement proper alerting rotation
  - Document post-incident review process
  - Maintain runbooks for common issues