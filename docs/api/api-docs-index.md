# API Documentation Index

## Service Overview

This service provides core functionality for the ACGS platform with constitutional compliance validation.

**Service**: API Documentation Index
**Port**: 8000
**Constitutional Hash**: `cdd01ef066bc6cf2`


<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


This index provides an overview and navigation links for the ACGS-2 API documentation set. Refer to these files for endpoint details, request schemas, and usage examples for all core services.

## Core Services

- **[Authentication API](authentication.md)** - User authentication, token management, and profile retrieval
- **[Constitutional AI API](constitutional-ai.md)** - Constitutional compliance validation, principle evaluation, and council operations

## Auxiliary Services

- **[Integration API](#api-overview)** - Cross-service workflows, data sharing, and event subscriptions
- **[Audit Logging API](#api-overview)** - Compliance records, user activity tracking, and event audit trails
- **[Alert Management API](#api-overview)** - Policy violation alerts, constitutional breach monitoring, and governance notifications

## System Services

- **[Health Checks & Metrics](#api-overview)** - Service status verification, performance metrics, and system health checks
- **[Service Discovery](#api-overview)** - API endpoints discovery, endpoint lifecycle management, and service registry access

## Reference Materials

- **[Core API Specification](#core-api-specification)** - ACGS-2 API base path conventions, response formats, and API versioning
- **[JWT Token Specification](#jwt-token-specification)** - JWT structure, token claims, and encryption standards
- **[Error Handling Guidelines](#error-handling)** - ACGS-2 API error codes, response structures, and client error guidelines
- **[Request Rate Limiting](#rate-limiting)** - User throttling, request quotas, and API rate limiting policies

## Example Clients

- **[Python SDK Example](#python-sdk)** - Python SDK installation, authentication, and sample workflow
- **[JavaScript Client Example](#javascript-client)** - JavaScript library integration, API request patterns, and error handling
- **[Go Client Library](#go-client)** - Go client setup, concurrent requests, and response parsing

## Additional Resources

- **[API Development Roadmap](#api-roadmap)** - Future endpoint expansions, planned features, and roadmap milestones
- **[Governance Policies Reference](#governance-policies)** - Data governance, policy lifecycle management, and constitutional compliance guidelines

For detailed system architecture, deployment guides, and full technical specifications, see the ACGS-2 project documentation repository.
## Performance Targets

- **Latency**: P99 ≤ 5ms for cached queries (latency_p99: ≤5ms)
- **Throughput**: ≥ 100 RPS sustained
- **Cache Hit Rate**: ≥ 85%
- **Test Coverage**: ≥ 80%
- **Availability**: 99.9% uptime
- **Constitutional Compliance**: 100% validation
