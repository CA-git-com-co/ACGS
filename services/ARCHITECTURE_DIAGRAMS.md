# ACGS-1 Lite Architecture Diagrams

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Version:** 1.0.0  
**Last Updated:** 2024-12-28

## 🎯 Overview

This document provides comprehensive architectural diagrams for ACGS-1 Lite, illustrating system topology, data flows, security boundaries, and operational patterns. These diagrams serve as the authoritative reference for understanding the system's design and implementation.

## 🏗️ System Architecture Overview

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ACGS-1 Lite System Architecture                       │
│                    Constitutional Hash: cdd01ef066bc6cf2                     │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────┐
                                    │   External      │
                                    │   Clients       │
                                    │                 │
                                    │ • Web Apps      │
                                    │ • Mobile Apps   │
                                    │ • AI Agents     │
                                    │ • Admin Tools   │
                                    └─────────┬───────┘
                                              │
                                              │ HTTPS/WSS
                                              │
                          ┌───────────────────┼───────────────────┐
                          │                   │                   │
                          ▼                   ▼                   ▼
                    ┌───────────┐    ┌─────────────┐    ┌─────────────┐
                    │   CDN     │    │Load Balancer│    │  API Gateway│
                    │           │    │   (nginx)   │    │             │
                    │ • Static  │    │             │    │ • Rate      │
                    │   Assets  │    │ • SSL Term  │    │   Limiting  │
                    │ • Caching │    │ • Health    │    │ • Auth      │
                    └───────────┘    │   Checks    │    │ • Routing   │
                                    └─────────┬───┘    └─────────┬───┘
                                              │                  │
                                              └─────────┬────────┘
                                                        │
                                ┌───────────────────────┼───────────────────────┐
                                │                       │                       │
                                ▼                       ▼                       ▼
                        ┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
                        │Policy Engine  │    │Evolution        │    │Audit Engine     │
                        │               │    │Oversight        │    │                 │
                        │Port: 8004     │    │                 │    │Port: 8003       │
                        │               │    │Port: 8002       │    │                 │
                        │• Constitutional│    │• Approval       │    │• Event Logging  │
                        │  Evaluation   │    │  Workflows      │    │• Hash Chaining  │
                        │• Safety Rules │◄───┤• Risk Assessment│◄───┤• Compliance     │
                        │• Caching      │    │• Rollback Plans │    │  Tracking       │
                        │• Partial Eval │    │• Human Review   │    │• S3 Archival    │
                        └───────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
                                │                      │                      │
                                └──────────────────────┼──────────────────────┘
                                                       │
                                            ┌─────────────────┐
                                            │Sandbox          │
                                            │Controller       │
                                            │                 │
                                            │Port: 8001       │
                                            │                 │
                                            │• gVisor Runtime │
                                            │• Firecracker VM │
                                            │• Seccomp Profile│
                                            │• Resource Limits│
                                            │• Syscall Monitor│
                                            └─────────┬───────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
                    ▼                                 ▼                                 ▼
            ┌───────────────┐                ┌───────────────┐                ┌───────────────┐
            │ Data Layer    │                │ Message Queue │                │ Object Storage│
            │               │                │               │                │               │
            │ PostgreSQL    │                │ Redpanda      │                │ MinIO/S3      │
            │               │                │ (Kafka)       │                │               │
            │• Audit Data   │                │               │                │• Archive Data │
            │• Metadata     │                │• Event Stream │                │• Backups      │
            │• User Data    │                │• Real-time    │                │• Static Assets│
            │• Config       │                │  Logs         │                │• Compliance   │
            └───────────────┘                │• Metrics      │                │  Data         │
                                            └───────────────┘                └───────────────┘

            ┌───────────────┐                ┌───────────────┐                ┌───────────────┐
            │ Cache Layer   │                │ Monitoring    │                │ Security      │
            │               │                │               │                │               │
            │ Redis         │                │ Prometheus    │                │ Vault         │
            │               │                │ Grafana       │                │ LDAP/SSO      │
            │• L2 Cache     │                │ AlertManager  │                │ TLS Certs     │
            │• Sessions     │                │               │                │ Secrets Mgmt  │
            │• Rate Limits  │                │• Metrics      │                │ Audit Logs    │
            │• Job Queue    │                │• Dashboards   │                │ Access Control│
            └───────────────┘                │• Alerting     │                └───────────────┘
                                            └───────────────┘
```

## 🔄 Data Flow Architecture

### Policy Evaluation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Policy Evaluation Data Flow                               │
└─────────────────────────────────────────────────────────────────────────────┘

    Client Request                    Policy Engine                    Response
         │                                 │                             ▲
         │ 1. Submit Policy Request        │                             │
         ├─────────────────────────────────┤                             │
         │                                 │                             │
         │ POST /v1/data/acgs/main/decision│                             │
         │ {                               │                             │
         │   "type": "constitutional_eval",│                             │
         │   "constitutional_hash": "cdd..",│                             │
         │   "action": "data.read_public", │                             │
         │   "context": {...}              │                             │
         │ }                               │                             │
         │                                 │                             │
         │                                 ▼                             │
         │                    ┌─────────────────────┐                    │
         │                    │ 2. Request          │                    │
         │                    │    Validation       │                    │
         │                    │                     │                    │
         │                    │ • Schema Check      │                    │
         │                    │ • Hash Verification │                    │
         │                    │ • Rate Limiting     │                    │
         │                    └─────────┬───────────┘                    │
         │                              │                                │
         │                              ▼                                │
         │                    ┌─────────────────────┐                    │
         │                    │ 3. Cache Check      │                    │
         │                    │    (L1 → L2)        │                    │
         │                    │                     │                    │
         │             Cache  │ • Generate Key      │  Cache Hit         │
         │              Miss  │ • Check L1 Cache    │     │              │
         │                 ┌──┤ • Check L2 Cache    │◄────┘              │
         │                 │  │ • xxhash Function   │                    │
         │                 │  └─────────┬───────────┘                    │
         │                 │            │                                │
         │                 ▼            ▼                                │
         │    ┌─────────────────────┐   │                                │
         │    │ 4. Partial          │   │                                │
         │    │    Evaluation       │   │                                │
         │    │                     │   │                                │
         │    │ • Safe Actions      │   │                                │
         │    │ • Dangerous Actions │   │                                │
         │    │ • Fast Path         │   │                                │
         │    └─────────┬───────────┘   │                                │
         │              │ Not Eligible  │                                │
         │              ▼               │                                │
         │    ┌─────────────────────┐   │                                │
         │    │ 5. Full OPA         │   │                                │
         │    │    Evaluation       │   │                                │
         │    │                     │   │                                │
         │    │ • Load Policies     │   │                                │
         │    │ • Execute Rego      │   │                                │
         │    │ • Constitutional    │   │                                │
         │    │   Compliance Check  │   │                                │
         │    └─────────┬───────────┘   │                                │
         │              │               │                                │
         │              ▼               │                                │
         │    ┌─────────────────────────┼─────────────────────┐          │
         │    │ 6. Audit Logging        │                     │          │
         │    │                         ▼                     │          │
         │    │    ┌─────────────────────────────────┐        │          │
         │    │    │        Audit Engine             │        │          │
         │    │    │                                 │        │          │
         │    │    │ • Event Creation                │        │          │
         │    │    │ • Hash Chain Update             │        │          │
         │    │    │ • Compliance Tracking           │        │          │
         │    │    │ • S3 Archival                   │        │          │
         │    │    └─────────────────────────────────┘        │          │
         │    │                                               │          │
         │    └───────────────────────────────────────────────┘          │
         │                              │                                │
         │                              ▼                                │
         │                    ┌─────────────────────┐                    │
         │                    │ 7. Response         │                    │
         │                    │    Generation       │                    │
         │                    │                     │                    │
         │                    │ • Allow/Deny        │                    │
         │                    │ • Compliance Score  │                    │
         │                    │ • Reasons           │                    │
         │                    │ • Conditions        │                    │
         │                    │ • Cache Update      │                    │
         │                    └─────────┬───────────┘                    │
         │                              │                                │
         │                              ▼                                │
         │ 8. JSON Response             │                                │
         │ {                            │                                │
         │   "allow": true,             │                                │
         │   "compliance_score": 0.96,  │                                │
         │   "constitutional_hash": "..",│                                │
         │   "reasons": [],             │                                │
         │   "evaluation_details": {...}│                                │
         │ }                            │                                │
         ├─────────────────────────────────────────────────────────────────┘
         │
         ▼
    Client Response
```

### Evolution Approval Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Evolution Approval Workflow                               │
└─────────────────────────────────────────────────────────────────────────────┘

Developer                Evolution Oversight              Policy Engine           Audit Engine
    │                           │                            │                       │
    │ 1. Submit Evolution       │                            │                       │
    │    Request                │                            │                       │
    ├───────────────────────────┤                            │                       │
    │                           │                            │                       │
    │ POST /evolution/request   │                            │                       │
    │ {                         │                            │                       │
    │   "agent_id": "agent_123",│                            │                       │
    │   "type": "minor_update", │                            │                       │
    │   "changes": {...},       │                            │                       │
    │   "rollback_plan": {...}  │                            │                       │
    │ }                         │                            │                       │
    │                           │                            │                       │
    │                           ▼                            │                       │
    │              ┌─────────────────────┐                   │                       │
    │              │ 2. Risk Assessment  │                   │                       │
    │              │                     │                   │                       │
    │              │ • Change Analysis   │                   │                       │
    │              │ • Risk Scoring      │                   │                       │
    │              │ • Dependency Check  │                   │                       │
    │              │ • Rollback Review   │                   │                       │
    │              └─────────┬───────────┘                   │                       │
    │                        │                               │                       │
    │                        ▼                               │                       │
    │              ┌─────────────────────┐                   │                       │
    │              │ 3. Approval Logic   │                   │                       │
    │              │                     │                   │                       │
    │              │ Score ≥95%: Auto    │                   │                       │
    │              │ Score 90-95%: Fast  │───────────────────┤                       │
    │              │ Score <90%: Human   │                   │                       │
    │              └─────────┬───────────┘                   │                       │
    │                        │                               │                       │
    │                        ▼                               │                       │
    │              ┌─────────────────────┐                   ▼                       │
    │              │ 4. Policy           │     ┌─────────────────────┐               │
    │              │    Validation       │────▶│ Constitutional      │               │
    │              │                     │     │ Policy Check        │               │
    │              │ • Constitutional    │     │                     │               │
    │              │   Compliance        │     │ • Safety Rules      │               │
    │              │ • Safety Review     │     │ • Resource Limits   │               │
    │              │ • Impact Analysis   │     │ • Change Validation │               │
    │              └─────────┬───────────┘     └─────────┬───────────┘               │
    │                        │                           │                           │
    │                        ▼                           ▼                           │
    │              ┌─────────────────────────────────────────────┐                   │
    │              │ 5. Decision & Audit Trail                  │───────────────────┤
    │              │                                             │                   │
    │              │ • Approval/Rejection Decision               │                   ▼
    │              │ • Conditions and Monitoring                 │     ┌─────────────────────┐
    │              │ • Audit Event Creation                      │     │ Audit Logging       │
    │              │ • Notification Generation                   │     │                     │
    │              └─────────┬───────────────────────────────────┘     │ • Decision Log      │
    │                        │                                         │ • Risk Assessment   │
    │                        ▼                                         │ • Compliance Check  │
    │ 6. Response            │                                         │ • Hash Chain Update │
    │                        │                                         └─────────────────────┘
    │ {                      │
    │   "request_id": "...", │
    │   "status": "approved",│
    │   "approval_type": ".", │
    │   "conditions": [...], │
    │   "valid_until": "..." │
    │ }                      │
    ├────────────────────────┘
    │
    ▼
Approved Evolution
```

### Audit Trail Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Audit Trail Data Flow                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Event Source              Audit Engine                PostgreSQL           S3/Archive
     │                         │                           │                    │
     │ 1. Audit Event          │                           │                    │
     ├─────────────────────────┤                           │                    │
     │                         │                           │                    │
     │ POST /audit/event       │                           │                    │
     │ {                       │                           │                    │
     │   "event_type": "...",  │                           │                    │
     │   "agent_id": "...",    │                           │                    │
     │   "action": "...",      │                           │                    │
     │   "result": "...",      │                           │                    │
     │   "metadata": {...}     │                           │                    │
     │ }                       │                           │                    │
     │                         │                           │                    │
     │                         ▼                           │                    │
     │            ┌─────────────────────┐                  │                    │
     │            │ 2. Event Processing │                  │                    │
     │            │                     │                  │                    │
     │            │ • Validation        │                  │                    │
     │            │ • Enrichment        │                  │                    │
     │            │ • Timestamp         │                  │                    │
     │            │ • Event ID Gen      │                  │                    │
     │            └─────────┬───────────┘                  │                    │
     │                      │                              │                    │
     │                      ▼                              │                    │
     │            ┌─────────────────────┐                  │                    │
     │            │ 3. Hash Calculation │                  │                    │
     │            │                     │                  │                    │
     │            │ • Previous Hash     │◄─────────────────┤                    │
     │            │ • Event Data Hash   │                  │                    │
     │            │ • Chain Update      │                  │                    │
     │            │ • Integrity Check   │                  │                    │
     │            └─────────┬───────────┘                  │                    │
     │                      │                              │                    │
     │                      ▼                              │                    │
     │            ┌─────────────────────────────────────────┼─────────────────┐  │
     │            │ 4. Dual Storage                         │                 │  │
     │            │                                         ▼                 │  │
     │            │    ┌─────────────────────┐    ┌─────────────────────┐    │  │
     │            │    │ Real-time Storage   │    │ Long-term Storage   │    │  │
     │            │    │                     │    │                     │    │  │
     │            │    │ • Active Events     │    │ • Historical Data   │────┼──┤
     │            │    │ • Query Interface   │    │ • Compliance        │    │  │
     │            │    │ • Hash Chain        │    │ • Archive           │    │  ▼
     │            │    │ • Metadata Index    │    │ • Backup            │    │ ┌─────────────────────┐
     │            │    └─────────────────────┘    └─────────────────────┘    │ │ S3 Object Storage   │
     │            └─────────────────────────────────────────────────────────┘ │                     │
     │                      │                              │                    │ • Immutable Store   │
     │                      ▼                              ▼                    │ • Compliance Logs   │
     │            ┌─────────────────────┐      ┌─────────────────────┐          │ • Legal Hold        │
     │            │ 5. Event Streaming  │      │ 6. Batch Archival  │          │ • Encryption        │
     │            │                     │      │                     │          └─────────────────────┘
     │            │ • Redpanda/Kafka    │      │ • Daily Batches     │
     │            │ • Real-time Feed    │      │ • Compression       │
     │            │ • Analytics Stream  │      │ • Deduplication     │
     │            │ • Alert Triggers    │      │ • Retention Policy  │
     │            └─────────────────────┘      └─────────────────────┘
     │                      │                              │
     │                      ▼                              ▼
     │ 7. Event ID Response │                 Archive Confirmation
     │                      │
     │ {                    │
     │   "event_id": "...", │
     │   "hash": "sha256:..",│
     │   "timestamp": "...", │
     │   "ingested": true    │
     │ }                    │
     ├──────────────────────┘
     │
     ▼
Event Confirmation
```

## 🏛️ Service Architecture

### Policy Engine Internal Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Policy Engine Internal Architecture                       │
└─────────────────────────────────────────────────────────────────────────────┘

                                    FastAPI Server
                                    Port: 8004
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │ Request Router  │   │ Middleware      │   │ Response        │
        │                 │   │ Stack           │   │ Handler         │
        │ • Route Match   │   │                 │   │                 │
        │ • Method Check  │   │ • CORS          │   │ • JSON Serial   │
        │ • Auth Guard    │   │ • Auth          │   │ • Error Format  │
        │ • Rate Limit    │   │ • Logging       │   │ • Headers       │
        └─────────┬───────┘   │ • Metrics       │   │ • Status Codes  │
                  │           │ • Validation    │   └─────────┬───────┘
                  │           └─────────┬───────┘             │
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        │
                              ┌─────────────────┐
                              │ Batch Processor │
                              │                 │
                              │ • Request Queue │
                              │ • Batch Window  │
                              │ • Parallel Exec │
                              │ • Result Merge  │
                              └─────────┬───────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │ Cache Manager   │   │ Partial         │   │ OPA Engine      │
        │                 │   │ Evaluator       │   │                 │
        │ L1: LRU Memory  │   │                 │   │ • Wasm Runtime  │
        │ ┌─────────────┐ │   │ • Safe Actions  │   │ • Policy Bundle │
        │ │Key│Value│LRU│ │   │ • Dangerous     │   │ • Rego Eval     │
        │ ├───┼─────┼───┤ │   │ • Pattern Match │   │ • Result Cache  │
        │ │...│ ... │...│ │   │ • Fast Path     │   │ • Error Handle  │
        │ └─────────────┘ │   └─────────────────┘   └─────────────────┘
        │                 │             │                       │
        │ L2: Redis       │             │                       │
        │ ┌─────────────┐ │             │                       │
        │ │Distributed  │ │             │                       │
        │ │Cache Store  │ │             │                       │
        │ │xxhash keys  │ │             │                       │
        │ └─────────────┘ │             │                       │
        └─────────┬───────┘             │                       │
                  │                     │                       │
                  └─────────────────────┼───────────────────────┘
                                        │
                              ┌─────────────────┐
                              │ Policy Decision │
                              │ Engine          │
                              │                 │
                              │ • Result Merge  │
                              │ • Score Calc    │
                              │ • Reason Gen    │
                              │ • Condition Set │
                              │ • Audit Trigger │
                              └─────────┬───────┘
                                        │
                                        ▼
                                ┌─────────────────┐
                                │ Metrics         │
                                │ Collector       │
                                │                 │
                                │ • Latency Track │
                                │ • Cache Stats   │
                                │ • Error Rates   │
                                │ • Throughput    │
                                │ • Prometheus    │
                                └─────────────────┘
```

### Sandbox Controller Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Sandbox Controller Internal Architecture                    │
└─────────────────────────────────────────────────────────────────────────────┘

                                    FastAPI Server
                                    Port: 8001
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │ Execution       │   │ Resource        │   │ Security        │
        │ Manager         │   │ Manager         │   │ Manager         │
        │                 │   │                 │   │                 │
        │ • Job Queue     │   │ • CPU Limits    │   │ • Seccomp       │
        │ • Status Track  │   │ • Memory Limits │   │ • Capabilities  │
        │ • Lifecycle     │   │ • Disk Limits   │   │ • Network       │
        │ • Cleanup       │   │ • Time Limits   │   │ • Filesystem    │
        └─────────┬───────┘   └─────────┬───────┘   └─────────┬───────┘
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        │
                              ┌─────────────────┐
                              │ Runtime         │
                              │ Dispatcher      │
                              │                 │
                              │ • Runtime Select│
                              │ • Config Gen    │
                              │ • Launch        │
                              │ • Monitor       │
                              └─────────┬───────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │ gVisor Runtime  │   │ Firecracker     │   │ Docker Runtime  │
        │                 │   │ Runtime         │   │                 │
        │ ┌─────────────┐ │   │                 │   │ • Container     │
        │ │ User Space  │ │   │ ┌─────────────┐ │   │ • Limited       │
        │ │ Kernel      │ │   │ │ MicroVM     │ │   │ • Development   │
        │ │             │ │   │ │ Isolation   │ │   │ • Testing       │
        │ │ • Syscall   │ │   │ │             │ │   │ • Legacy        │
        │ │   Filter    │ │   │ │ • Hardware  │ │   └─────────────────┘
        │ │ • Memory    │ │   │ │   Virtual   │ │             │
        │ │   Isolation │ │   │ │ • Boot Fast │ │             │
        │ │ • Network   │ │   │ │ • Secure    │ │             │
        │ │   Namespace │ │   │ └─────────────┘ │             │
        │ └─────────────┘ │   └─────────────────┘             │
        └─────────┬───────┘             │                     │
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        │
                              ┌─────────────────┐
                              │ Monitoring      │
                              │ & Logging       │
                              │                 │
                              │ • Syscall Log   │
                              │ • Resource Use  │
                              │ • Performance   │
                              │ • Violations    │
                              │ • Audit Trail   │
                              └─────────────────┘
```

## 🌐 Network Architecture

### Network Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Network Architecture                               │
└─────────────────────────────────────────────────────────────────────────────┘

Internet
   │
   │ Port 443 (HTTPS)
   │ Port 80 (HTTP → Redirect)
   │
   ▼
┌─────────────────┐
│ Load Balancer   │ 
│ (nginx)         │ 
│                 │ 
│ • SSL Term      │
│ • Rate Limiting │
│ • Health Checks │
└─────────┬───────┘
          │
          │ Internal Network
          │ 172.20.0.0/16
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Application Network                                  │
│                           172.20.1.0/24                                     │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│ │Policy Engine│  │Evolution    │  │Audit Engine │  │Sandbox      │         │
│ │   :8004     │  │Oversight    │  │   :8003     │  │Controller   │         │
│ │             │  │   :8002     │  │             │  │   :8001     │         │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                │               │
│         └────────────────┼────────────────┼────────────────┘               │
│                          │                │                                │
└──────────────────────────┼────────────────┼────────────────────────────────┘
                           │                │
                           ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Infrastructure Network                                │
│                           172.20.2.0/24                                     │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│ │PostgreSQL   │  │Redis        │  │Redpanda     │  │MinIO        │         │
│ │   :5432     │  │   :6379     │  │   :9092     │  │   :9000     │         │
│ │             │  │             │  │             │  │             │         │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         Monitoring Network                                   │
│                           172.20.3.0/24                                     │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│ │Prometheus   │  │Grafana      │  │AlertManager │  │Log          │         │
│ │   :9090     │  │   :3000     │  │   :9093     │  │Aggregator   │         │
│ │             │  │             │  │             │  │   :5044     │         │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security Zones

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Security Zones                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              DMZ Zone                                        │
│                        (Untrusted Network)                                   │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                           │
│ │Load Balancer│  │Web Proxy    │  │Rate Limiter │                           │
│ │             │  │             │  │             │                           │
│ │ • SSL Term  │  │ • Static    │  │ • DDoS Prot │                           │
│ │ • WAF       │  │   Assets    │  │ • Traffic   │                           │
│ │ • DDoS Prot │  │ • Caching   │  │   Shape     │                           │
│ └─────────────┘  └─────────────┘  └─────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                               Firewall Rules
                               • Port 443 HTTPS
                               • Port 80 HTTP
                               • Health Checks
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Application Zone                                    │
│                        (Semi-Trusted Network)                               │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│ │Policy Engine│  │Evolution    │  │Audit Engine │  │Sandbox      │         │
│ │             │  │Oversight    │  │             │  │Controller   │         │
│ │ • mTLS      │  │ • JWT Auth  │  │ • Crypto    │  │ • Isolation │         │
│ │ • Rate Lim  │  │ • RBAC      │  │   Integrity │  │ • Seccomp   │         │
│ │ • Input Val │  │ • Audit Log │  │ • Immutable │  │ • Syscall   │         │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                               Network Policies
                               • Service Mesh
                               • Encrypted Comms
                               • Access Control
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Data Zone                                         │
│                         (Trusted Network)                                   │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│ │PostgreSQL   │  │Redis        │  │Redpanda     │  │MinIO        │         │
│ │             │  │             │  │             │  │             │         │
│ │ • Encrypt   │  │ • Auth Req  │  │ • TLS       │  │ • Object    │         │
│ │   at Rest   │  │ • Memory    │  │ • SASL      │  │   Lock      │         │
│ │ • Access    │  │   Encrypt   │  │ • Audit     │  │ • Versioning│         │
│ │   Control   │  │ • Backup    │  │ • Retention │  │ • Compliance│         │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                               Isolated Network
                               • No Internet Access
                               • Encrypted Storage
                               • Audit Logging
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Management Zone                                      │
│                        (Admin Network)                                      │
│                                                                             │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│ │Prometheus   │  │Grafana      │  │Vault        │  │LDAP/SSO     │         │
│ │             │  │             │  │             │  │             │         │
│ │ • Metrics   │  │ • Dashboards│  │ • Secrets   │  │ • Identity  │         │
│ │ • Alerting  │  │ • Admin UI  │  │ • PKI       │  │ • Federation│         │
│ │ • TSDB      │  │ • RBAC      │  │ • Audit     │  │ • MFA       │         │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Deployment Architecture

### Container Orchestration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Container Deployment Architecture                     │
└─────────────────────────────────────────────────────────────────────────────┘

                               Docker Compose
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │ Application   │ │Infrastructure │ │ Monitoring    │
            │ Services      │ │ Services      │ │ Services      │
            │               │ │               │ │               │
            │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │
            │ │Policy     │ │ │ │PostgreSQL │ │ │ │Prometheus │ │
            │ │Engine     │ │ │ │           │ │ │ │           │ │
            │ │ ┌───────┐ │ │ │ │ • ACID    │ │ │ │ • TSDB    │ │
            │ │ │L1Cache│ │ │ │ │ • WAL     │ │ │ │ • Rules   │ │
            │ │ │Memory │ │ │ │ │ • Backup  │ │ │ │ • Alerts  │ │
            │ │ └───────┘ │ │ │ └───────────┘ │ │ └───────────┘ │
            │ └───────────┘ │ │               │ │               │
            │               │ │ ┌───────────┐ │ │ ┌───────────┐ │
            │ ┌───────────┐ │ │ │Redis      │ │ │ │Grafana    │ │
            │ │Evolution  │ │ │ │           │ │ │ │           │ │
            │ │Oversight  │ │ │ │ • L2Cache │ │ │ │ • Dashboard│ │
            │ │           │ │ │ │ • Session │ │ │ │ • Alerting│ │
            │ │ • Risk    │ │ │ │ • Queue   │ │ │ │ • RBAC    │ │
            │ │   Assess  │ │ │ └───────────┘ │ │ └───────────┘ │
            │ │ • Approval│ │ │               │ │               │
            │ └───────────┘ │ │ ┌───────────┐ │ └───────────────┘
            │               │ │ │Redpanda   │ │
            │ ┌───────────┐ │ │ │           │ │
            │ │Audit      │ │ │ │ • Kafka   │ │
            │ │Engine     │ │ │ │ • Stream  │ │
            │ │           │ │ │ │ • Partition│ │
            │ │ • Hash    │ │ │ └───────────┘ │
            │ │   Chain   │ │ │               │
            │ │ • Integrity│ │ │ ┌───────────┐ │
            │ └───────────┘ │ │ │MinIO/S3   │ │
            │               │ │ │           │ │
            │ ┌───────────┐ │ │ │ • Object  │ │
            │ │Sandbox    │ │ │ │   Storage │ │
            │ │Controller │ │ │ │ • Archive │ │
            │ │           │ │ │ │ • Backup  │ │
            │ │ • gVisor  │ │ │ └───────────┘ │
            │ │ • Firecrk │ │ └───────────────┘
            │ │ • Seccomp │ │
            │ └───────────┘ │
            └───────────────┘
```

### High Availability Setup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      High Availability Architecture                          │
└─────────────────────────────────────────────────────────────────────────────┘

                                Load Balancer
                              (nginx/HAProxy)
                                     │
                              Health Checks
                              Round Robin
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │   Node 1      │ │   Node 2      │ │   Node 3      │
            │               │ │               │ │               │
            │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │
            │ │Policy     │ │ │ │Policy     │ │ │ │Policy     │ │
            │ │Engine     │ │ │ │Engine     │ │ │ │Engine     │ │
            │ │ • Active  │ │ │ │ • Active  │ │ │ │ • Active  │ │
            │ │ • L1Cache │ │ │ │ • L1Cache │ │ │ │ • L1Cache │ │
            │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │
            │               │ │               │ │               │
            │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │
            │ │Evolution  │ │ │ │Evolution  │ │ │ │Evolution  │ │
            │ │Oversight  │ │ │ │Oversight  │ │ │ │Oversight  │ │
            │ │ • Active  │ │ │ │ • Standby │ │ │ │ • Standby │ │
            │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │
            │               │ │               │ │               │
            │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │
            │ │Audit      │ │ │ │Audit      │ │ │ │Audit      │ │
            │ │Engine     │ │ │ │Engine     │ │ │ │Engine     │ │
            │ │ • Primary │ │ │ │ • Replica │ │ │ │ • Replica │ │
            │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │
            └───────────────┘ └───────────────┘ └───────────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                              Shared Storage
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │PostgreSQL     │ │Redis Cluster  │ │MinIO Cluster  │
            │ Master/Slave  │ │               │ │               │
            │               │ │ ┌───────────┐ │ │ ┌───────────┐ │
            │ • Replication │ │ │ Master    │ │ │ │ Node 1    │ │
            │ • Failover    │ │ │ ┌───────┐ │ │ │ │ ┌───────┐ │ │
            │ • Backup      │ │ │ │Sentinel│ │ │ │ │ │Bucket │ │ │
            │               │ │ │ └───────┘ │ │ │ │ │ │Replica│ │ │
            │ ┌───────────┐ │ │ └───────────┘ │ │ │ │ └───────┘ │ │
            │ │ Primary   │ │ │               │ │ │ └───────────┘ │
            │ │ Instance  │ │ │ ┌───────────┐ │ │               │
            │ └───────────┘ │ │ │ Slave 1   │ │ │ ┌───────────┐ │
            │               │ │ └───────────┘ │ │ │ Node 2    │ │
            │ ┌───────────┐ │ │               │ │ │ (Replica) │ │
            │ │ Read      │ │ │ ┌───────────┐ │ │ └───────────┘ │
            │ │ Replica   │ │ │ │ Slave 2   │ │ │               │
            │ └───────────┘ │ │ └───────────┘ │ │ ┌───────────┐ │
            └───────────────┘ └───────────────┘ │ │ Node 3    │ │
                                                │ │ (Replica) │ │
                                                │ └───────────┘ │
                                                └───────────────┘
```

## 📊 Monitoring Architecture

### Observability Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Observability Architecture                           │
└─────────────────────────────────────────────────────────────────────────────┘

            Application Services                  Monitoring Stack
                    │                                    │
        ┌───────────┼───────────┐                       │
        │           │           │                       │
        ▼           ▼           ▼                       ▼
┌───────────┐ ┌──────────┐ ┌──────────┐     ┌─────────────────┐
│Policy     │ │Evolution │ │Audit     │     │ Metrics         │
│Engine     │ │Oversight │ │Engine    │     │ Collection      │
│           │ │          │ │          │     │                 │
│ Metrics   │ │ Metrics  │ │ Metrics  │────▶│ ┌─────────────┐ │
│ ┌───────┐ │ │ ┌──────┐ │ │ ┌──────┐ │     │ │Prometheus   │ │
│ │Latency│ │ │ │Risk  │ │ │ │Hash  │ │     │ │             │ │
│ │P99/P95│ │ │ │Score │ │ │ │Chain │ │     │ │ • Scraping  │ │
│ │Cache  │ │ │ │Apprv │ │ │ │Intgty│ │     │ │ • TSDB      │ │
│ │Hit    │ │ │ │Rate  │ │ │ │Rate  │ │     │ │ • Rules     │ │
│ └───────┘ │ │ └──────┘ │ │ └──────┘ │     │ │ • Alerts    │ │
└───────────┘ └──────────┘ └──────────┘     │ └─────────────┘ │
                    │                       └─────────┬───────┘
                    │ Logs                            │
                    ▼                                 │
        ┌─────────────────────┐                      │
        │ Log Aggregation     │                      │
        │                     │                      │
        │ ┌─────────────────┐ │                      │
        │ │ Structured Logs │ │                      │
        │ │                 │ │                      ▼
        │ │ • JSON Format   │ │           ┌─────────────────┐
        │ │ • Correlation   │ │           │ Visualization   │
        │ │ • Sampling      │ │           │                 │
        │ │ • Retention     │ │           │ ┌─────────────┐ │
        │ └─────────────────┘ │           │ │Grafana      │ │
        │                     │           │ │             │ │
        │ ┌─────────────────┐ │           │ │ • Dashboards│ │
        │ │ Log Storage     │ │           │ │ • Alerting  │ │
        │ │                 │ │           │ │ • RBAC      │ │
        │ │ • Elasticsearch │ │           │ │ • Variables │ │
        │ │ • Retention     │ │           │ │ • Plugins   │ │
        │ │ • Indexing      │ │           │ └─────────────┘ │
        │ │ • Search        │ │           └─────────┬───────┘
        │ └─────────────────┘ │                     │
        └─────────────────────┘                     │
                    │                               │
                    │ Traces                        │
                    ▼                               ▼
        ┌─────────────────────┐           ┌─────────────────┐
        │ Distributed         │           │ Alerting        │
        │ Tracing             │           │                 │
        │                     │           │ ┌─────────────┐ │
        │ ┌─────────────────┐ │           │ │AlertManager │ │
        │ │ Jaeger/Zipkin   │ │           │ │             │ │
        │ │                 │ │           │ │ • Routing   │ │
        │ │ • Span Collection│ │           │ │ • Grouping  │ │
        │ │ • Service Map   │ │           │ │ • Silencing │ │
        │ │ • Performance   │ │           │ │ • Templates │ │
        │ │ • Dependencies  │ │           │ └─────────────┘ │
        │ └─────────────────┘ │           │                 │
        └─────────────────────┘           │ ┌─────────────┐ │
                                          │ │Notification │ │
                                          │ │             │ │
                                          │ │ • Slack     │ │
                                          │ │ • Email     │ │
                                          │ │ • PagerDuty │ │
                                          │ │ • Webhook   │ │
                                          │ └─────────────┘ │
                                          └─────────────────┘
```

---

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Architecture Documentation Version:** 1.0.0  
**Last Updated:** 2024-12-28