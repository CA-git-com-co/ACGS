# ACGS-1 Evolutionary Computation Service

## Overview

The Evolutionary Computation (EC) Service is an enterprise-grade WINA-optimized oversight and governance platform that provides advanced evolutionary computation algorithms, constitutional compliance verification, and intelligent performance optimization for the ACGS-PGP system.

**Service Port**: 8006
**Service Version**: 3.0.0 (Phase 3 Production)
**Constitutional Hash**: `cdd01ef066bc6cf2`
**Health Check**: http://localhost:8006/health

## Core Features

- **WINA-Optimized Oversight:** Advanced WINA optimization for resource allocation and governance.
- **Advanced Evolutionary Computation Algorithms:** A suite of algorithms for genetic and multi-objective optimization.
- **AlphaEvolve Integration:** Integration with the AlphaEvolve governance framework for continuous optimization.
- **Enterprise Features:** Advanced analytics, real-time monitoring, and seamless integration with other ACGS services.

## API Endpoints

- A comprehensive set of API endpoints are available for WINA oversight, advanced optimization, AlphaEvolve integration, performance monitoring, evolutionary computation, reporting, and system management. Please refer to the OpenAPI documentation at `/openapi.json` for a complete list of endpoints and their specifications.

## Configuration

- The service is configured through environment variables. Please refer to the `.env.example` file for a complete list of configuration options.

## Installation & Deployment

- The service can be run locally using Docker or deployed to a Kubernetes cluster. Please refer to the `docker-compose.yml` and `kubernetes/` directory for deployment configurations.

## Testing

- The service includes a comprehensive suite of unit, integration, and performance tests. Please refer to the `tests/` directory for more information.
