# ACGS Architecture Gap Analysis Report

**Date:** 2025-06-26

**Author:** Gemini

## 1. Executive Summary

This report details the gap analysis between the current ACGS-PGP 7-service architecture and the proposed 8-service enterprise architecture outlined in the `GEMINI.md` specification. The analysis identifies significant differences in service architecture, technology stack, security, performance, and governance mechanisms. The migration to the proposed architecture represents a major evolution of the ACGS platform, requiring a carefully planned and phased implementation.

## 2. Current State Assessment (ACGS-PGP)

The current architecture, as defined in `docker-compose.yml`, consists of seven core microservices, each with a specific port:

- **Authentication Service (auth_service):** Port 8000
- **Constitutional AI Service (ac_service):** Port 8001
- **Integrity Service (integrity_service):** Port 8002
- **Formal Verification Service (fv_service):** Port 8003
- **Governance Synthesis Service (gs_service):** Port 8004
- **Policy Governance Service (pgc_service):** Port 8005
- **Evolutionary Computation Service (ec_service):** Port 8006

**Key characteristics of the current architecture:**

- **Infrastructure:** PostgreSQL, Redis, HAProxy, and Open Policy Agent (OPA) on port 8181.
- **AI Models:** Not explicitly defined in the `docker-compose.yml`, but `GEMINI.md` suggests a stack of Google Gemini, DeepSeek-R1, NVIDIA Qwen, and Nano-vLLM.
- **Security:** Relies on JWT-based authentication and PGP-based constitutional hash validation (`cdd01ef066bc6cf2`).
- **Constitutional Compliance:** The constitutional hash is consistently used across the `ac_service`, `pgc_service`, and `opa` services.

## 3. Proposed State (GEMINI.md)

The `GEMINI.md` specification proposes a more advanced, scalable, and resilient 8-service architecture:

- **Authentication Service:** Ports 8000-8009
- **Constitutional AI Service:** Ports 8010-8019
- **Integrity Service:** Ports 8020-8029
- **Formal Verification Service:** Ports 8030-8039
- **Governance Synthesis Service:** Ports 8040-8049
- **Policy Governance Service:** Ports 8050-8059
- **Evolutionary Computation Service:** Ports 8060-8069
- **Model Orchestrator Service (New):** Ports 8070-8079

**Key characteristics of the proposed architecture:**

- **Infrastructure:** Linkerd service mesh, DragonflyDB (as a Redis replacement), Apache Pulsar/Redpanda for messaging, and CockroachDB for the database.
- **AI Models:** A significantly expanded and managed set of AI models, including OpenAI o3, Gemini 2.5 Pro/Flash, Qwen 2.5 VL, and Llama 3.1 405B, all managed by the new `Model Orchestrator` service.
- **Security:** A forward-looking security posture with Post-Quantum Cryptography (NIST ML-KEM, ML-DSA), a Zero-Trust Architecture, Confidential Computing (Intel TDX), and immutable audit trails using Hedera Hashgraph.
- **Performance:** A massive leap in performance targets, from 1,000 RPS to 15,000+ RPS and from 2-second latency to sub-50ms P50 latency.
- **Democratic Governance:** Direct integration with established democratic governance platforms like Pol.is and Decidim.

## 4. Gap Analysis

### 4.1. Service Architecture

| Feature                 | Current State (ACGS-PGP) | Proposed State (GEMINI.md)                | Gap & Migration Requirements                                                                                                                                                                                                |
| ----------------------- | ------------------------ | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Number of Services**  | 7                        | 8                                         | **Gap:** Introduction of the new `Model Orchestrator` service. <br> **Migration:** A new service needs to be designed, developed, and integrated into the existing architecture.                                            |
| **Service Scalability** | Single port per service  | Port ranges per service (e.g., 8000-8009) | **Gap:** The proposed architecture is designed for horizontal scalability. <br> **Migration:** Services need to be adapted to run in a containerized environment (like Kubernetes) and managed by a service mesh (Linkerd). |

### 4.2. Technology Stack

| Component | Current State (ACGS-PGP) | Proposed State (GEMINI.md) | Gap & Migration Requirements -
| **Database** | PostgreSQL | CockroachDB | **Gap:** Shift from a traditional relational database to a distributed SQL database. <br> **Migration:** Requires a data migration strategy and changes to the data access layer in each service. -
| **Caching** | Redis | DragonflyDB | **Gap:** Move to a high-performance, Redis-compatible in-memory datastore. <br> **Migration:** Relatively straightforward due to API compatibility, but requires infrastructure changes. -
| **Messaging** | None (Direct service-to-service communication) | Apache Pulsar / Redpanda | **Gap:** Introduction of a dedicated event and messaging layer. <br> **Migration:** Requires services to be refactored to use a message queue for asynchronous communication, which is a significant architectural change. -
| **Service Mesh** | None (HAProxy for load balancing) | Linkerd + eBPF | **Gap:** Introduction of a service mesh for observability, security, and reliability. <br> **Migration:** Requires deploying Linkerd and integrating all services into the mesh. -
| **AI Model Management** | Ad-hoc | Model Orchestrator Service | **Gap:** Centralized, dynamic management of AI models. <br> **Migration:** Requires the development of the `Model Orchestrator` service and the refactoring of existing services to use it. -

### 4.3. Security

| Feature | Current State (ACGS-PGP) | Proposed State (GEMINI.md) | Gap & Migration Requirements -
| **Cryptography** | PGP-based hash validation | Post-Quantum Cryptography (ML-KEM, ML-DSA) | **Gap:** A fundamental shift in cryptographic algorithms to address future threats. <br> **Migration:** Requires integrating new cryptographic libraries and updating all services that handle sensitive data. -
| **Audit Trail** | Standard logging | Hedera Hashgraph for immutable records | **Gap:** Use of a distributed ledger for a tamper-proof audit trail. <br> **Migration:** Requires integrating the Hedera Hashgraph SDK and designing a system for recording governance events on the ledger. -
| **Architecture** | Standard microservices | Zero-Trust Architecture | **Gap:** A more stringent security model that assumes no implicit trust. <br> **Migration:** Requires implementing stricter access controls, service authentication, and authorization mechanisms, likely leveraging the service mesh. -

### 4.4. Performance

| Feature | Current State (ACGS-PGP) | Proposed State (GEMINI.md) | Gap & Migration Requirements -
| **Throughput** | 1,000 RPS | 15,000+ RPS | **Gap:** A 15x increase in throughput. <br> **Migration:** Requires a complete re-architecture for performance, including the adoption of the proposed high-performance infrastructure and significant optimization of each service. |
| **Latency** | <= 2s (p95) | <50ms (p50), <400ms (p99) | **Gap:** A dramatic reduction in latency. <br> **Migration:** Requires the new infrastructure, optimized code, and a focus on reducing inter-service communication overhead. |

### 4.5. Governance

| Feature | Current State (ACGS-PGP) | Proposed State (GEMINI.md) | Gap & Migration Requirements -
| **Democratic Governance** | Limited to internal mechanisms | Integration with Pol.is and Decidim | **Gap:** Direct integration with external democratic governance platforms. <br> **Migration:** Requires developing new integrations and APIs to connect with these platforms. -

## 5. Conclusion

The migration from the current ACGS-PGP architecture to the proposed enterprise architecture in `GEMINI.md` is a significant undertaking that will transform the ACGS platform into a highly scalable, secure, and performant system. The gaps identified in this report highlight the key areas that will require significant development and migration efforts. A phased approach, as outlined in the `GEMINI.md` document, is essential for a successful implementation.
