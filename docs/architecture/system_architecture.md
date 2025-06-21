# ACGS-1 System Architecture

This document provides a comprehensive overview of the ACGS-1 system architecture.

## Overview

ACGS-1 is a blockchain-focused constitutional governance platform with 8 core services and event-driven architecture:

1. **Auth Service (Port 8000)** - Authentication & Authorization
2. **AC Service (Port 8001)** - Constitutional AI Management
3. **Integrity Service (Port 8002)** - Cryptographic Integrity
4. **FV Service (Port 8003)** - Formal Verification
5. **GS Service (Port 8004)** - Governance Synthesis
6. **PGC Service (Port 8005)** - Policy Governance & Compliance
7. **EC Service (Port 8006)** - Executive Council/Oversight
8. **DGM Service (Port 8007)** - Darwin Gödel Machine Self-Improvement

## Event-Driven Architecture

The system implements event-driven architecture with:

- **Message Broker**: NATS for asynchronous communication
- **Service Mesh**: Istio for traffic management and observability
- **Event Sourcing**: Constitutional compliance events and audit trails
- **CQRS Pattern**: Command Query Responsibility Segregation for performance

## Quantumagi Blockchain Integration

- **Constitution Hash**: cdd01ef066bc6cf2
- **Deployment**: Solana Devnet
- **Programs**: quantumagi-core, appeals, logging
