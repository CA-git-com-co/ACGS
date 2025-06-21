# ACGS-1 Deployment Guide

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- Solana CLI 1.18.22
- Anchor 0.29.0

## Host-Based Deployment

1. Install dependencies
2. Configure environment variables
3. Start services in order: Auth → AC → Integrity → FV → GS → PGC → EC
4. Verify health checks

## Docker Deployment

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```
