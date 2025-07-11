# Blackboard Service

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides comprehensive documentation for the **Blackboard Service**. This service is a core component of the ACGS-2 platform, providing a centralized, Redis-based blackboard for constitutional knowledge sharing, agent coordination, and performance caching.

- **Service Name**: Blackboard Service
- **Underlying Technology**: Redis
- **Port**: 6389 (Standard Redis Port)

Unlike other services, the Blackboard Service does not expose a REST API. Services interact with it directly through a Redis client.

## 2. Functionality

The Blackboard Service is essential for multi-agent coordination and constitutional compliance, providing the following key functions:

- **Constitutional Context Propagation**: Ensures that the current constitutional context is available to all agents and services.
- **Agent Coordination**: Acts as a central message bus and knowledge repository for agents to share information, post tasks, and track the state of complex governance workflows.
- **Performance Caching**: Caches frequently accessed data and constitutional metadata to meet the system's strict performance targets.

## 3. Performance Targets

- **P99 Latency**: <5ms
- **Throughput**: >1000 RPS
- **Cache Hit Rate**: >85%
- **Availability**: 99.99%
- **Constitutional Compliance**: 97% (Verified)

## 4. Connection Details

Services connect to the Blackboard Service using a standard Redis client. The connection details are managed through the central configuration service and should not be hardcoded. All interactions are subject to the system's constitutional validation and audit trail logging.

## 5. Related Information

- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
