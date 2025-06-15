# ACGS-1 Project Commands and Guidelines

This document provides standardized commands and coding guidelines for the ACGS-1 Constitutional Governance System project. All team members must follow these standards to ensure code quality and consistency.

## Build/Test/Lint Commands

### Python Testing
```bash
# Run all Python tests with verbose output and stop on first failure
pytest -xvs tests/

# Run a specific test function within a file
pytest -xvs tests/test_specific_file.py::test_function

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

### JavaScript Testing
```bash
# Run all JavaScript/TypeScript tests
npm test

# Run only council hook-related tests
npm run test:hooks

# Run tests with coverage
npm test -- --coverage
```

### Blockchain Testing
```bash
# Run Solana/Anchor tests with extended timeout (16.7 minutes)
cd blockchain && yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/specific_test.ts
```

### Linting & Type Checking
```bash
# Python linting
ruff check .

# TypeScript type checking
npm run typecheck

# Solana/Anchor linting
cd blockchain && anchor lint
```

### Deployment
```bash
# Deploy and initialize the constitutional governance smart contracts
cd blockchain && yarn run initialize-constitution
```

### CI/CD Validation
```bash
# Execute the complete CI/CD test suite
./scripts/ci_cd_test.sh
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

- **Performance**:
  - Memoize expensive calculations with useMemo
  - Use useCallback for event handlers passed as props
  - Implement code splitting for large component trees

### Rust/Solana
- **Safety**:
  - Enable overflow checks in all environments
  - Use proper error types and propagation
  - Never use unsafe code without review
- **Documentation**:
  - Document all public functions with rustdoc
  - Include security considerations in comments
  - Explain complex algorithms with diagrams/comments
- **Testing**:
  - 100% test coverage for critical contract functions
  - Include property-based testing for mathematical operations
  - Test all error conditions explicitly

## Naming Conventions

- **Files**:
  - React components: `ComponentName.tsx` (PascalCase)
  - Hooks: `useHookName.ts` (camelCase)
  - Utilities: `utilityName.ts` (camelCase)
  - Python modules: `module_name.py` (snake_case)

- **Variables**:
  - Regular variables: `camelCase` (JS/TS), `snake_case` (Python)
  - Constants: `SCREAMING_SNAKE_CASE`
  - Private class members: `_camelCaseWithUnderscore` (JS/TS), `_snake_case` (Python)
  - Boolean variables: Use prefix like `is_`, `has_`, `should_`

- **Functions/Methods**:
  - Use verb phrases describing actions
  - Examples: `validatePolicy()`, `getPrincipleById()`, `calculateComplianceScore()`

- **Types/Interfaces**:
  - Use PascalCase with descriptive names
  - Examples: `ConstitutionalPrinciple`, `GovernanceState`
  - Avoid generic names like `Manager`, `Processor`, `Handler`

- **Test Files**:
  - Python: `test_module_name.py`
  - TypeScript/JavaScript: `module_name.test.ts`
  - Group tests logically by feature/function

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

- **TypeScript**:
  - Implement service-specific error boundaries
  - Use proper loading states with timeouts
  - Include error recovery mechanisms
  - Provide helpful error messages to users
  - Log detailed error information for debugging

- **Solana**:
  - Define explicit error enum for all possible failure modes
  - Include descriptive error messages
  - Implement transaction retry logic for network issues
  - Validate all inputs before processing
  - Use proper error propagation with `?` operator

## Security Best Practices

- **Input Validation**:
  - Validate all inputs at service boundaries
  - Use strict schemas for data validation
  - Sanitize user-provided data before use

- **Authentication/Authorization**:
  - Implement proper role-based access control
  - Use short-lived JWT tokens
  - Validate permissions for all governance actions

- **Smart Contract Security**:
  - Follow Anchor security best practices
  - Implement comprehensive ownership checks
  - Never use raw lamport transfers without validation

- **API Security**:
  - Use HTTPS for all communications
  - Implement rate limiting
  - Add CSRF protection for web endpoints