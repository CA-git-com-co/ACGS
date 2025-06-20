# ACGS-1 Getting Started Guide

Welcome to the ACGS-1 Constitutional Governance System! This comprehensive guide will help you get started with the system, whether you're a developer, operator, or end-user.

## 🎯 Quick Start (5 Minutes)

### Prerequisites Check
```bash
# Check required software
python --version    # Should be 3.9+
node --version      # Should be 18+
docker --version    # Should be 24.0+
psql --version      # Should be 15+
redis-cli --version # Should be 7+
```

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# Quick setup script
./scripts/setup/quick_start.sh
```

### 2. Start Core Services
```bash
# Start with Docker Compose (Recommended)
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Or start manually
./scripts/start_all_services.sh
```

### 3. Verify Installation
```bash
# Check all services are running
./scripts/comprehensive_health_check.py

# Expected output: All services should show "healthy" status
```

### 4. Access the System
- **Governance Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs (Constitutional AI)
- **Monitoring Dashboard**: http://localhost:3001 (Grafana)

## 👥 User Types and Workflows

### For Developers

#### Setting Up Development Environment
```bash
# 1. Install development dependencies
pip install -r config/requirements.txt
npm install --prefix applications/governance-dashboard

# 2. Configure development environment
cp config/env/.env.example .env
# Edit .env with your configuration

# 3. Set up pre-commit hooks
pre-commit install

# 4. Run tests to verify setup
python -m pytest tests/unit/ -v
```

#### Your First API Call
```python
import httpx
import asyncio

async def test_constitutional_ai():
    async with httpx.AsyncClient() as client:
        # Test health endpoint
        response = await client.get("http://localhost:8001/health")
        print(f"Health Status: {response.json()['status']}")
        
        # Test constitutional validation
        validation_response = await client.post(
            "http://localhost:8001/api/v1/constitutional/validate",
            json={
                "policy": "Citizens have the right to privacy and data protection",
                "principles": ["privacy", "transparency", "accountability"]
            }
        )
        print(f"Constitutional Compliance: {validation_response.json()}")

# Run the test
asyncio.run(test_constitutional_ai())
```

#### Development Workflow
1. **Create Feature Branch**: `git checkout -b feature/your-feature`
2. **Write Tests**: Add tests in `tests/` directory
3. **Implement Feature**: Follow ACGS-1 coding standards
4. **Run Tests**: `python -m pytest tests/ -v`
5. **Check Compliance**: `./scripts/validation/security_audit.py`
6. **Submit PR**: Create pull request with comprehensive description

### For Operators

#### Production Deployment Checklist
```bash
# 1. Environment preparation
./scripts/deployment/prepare_production_environment.sh

# 2. Security hardening
./scripts/security/harden_production_deployment.sh

# 3. Deploy services
./scripts/deployment/deploy_production_complete.sh

# 4. Verify deployment
./scripts/validation/validate_production_deployment.sh

# 5. Set up monitoring
./scripts/monitoring/setup_production_monitoring.sh
```

#### Daily Operations
```bash
# Morning health check
./scripts/comprehensive_health_check.py

# Check system metrics
curl http://localhost:9090/api/v1/query?query=up

# Review overnight logs
grep ERROR logs/*.log | tail -20

# Backup database
./scripts/backup/backup_database_comprehensive.sh
```

#### Troubleshooting Quick Reference
```bash
# Service not responding
curl http://localhost:8001/health
pkill -f "uvicorn.*8001"
cd services/core/constitutional-ai/ac_service
uvicorn app.main:app --host 0.0.0.0 --port 8001 &

# Database issues
psql $DATABASE_URL -c "SELECT 1;"
docker restart acgs_postgres_db

# Cache issues
redis-cli ping
redis-cli FLUSHALL
```

### For End-Users (Governance Dashboard)

#### Accessing the Dashboard
1. **Navigate to**: http://localhost:3000
2. **Login**: Use your ACGS-1 credentials
3. **Dashboard Overview**: Review system status and recent activities

#### Creating Your First Policy
1. **Navigate to Policy Creation**:
   - Click "Create New Policy" in the dashboard
   - Select policy type (Regulatory, Administrative, Constitutional)

2. **Fill Policy Details**:
   ```
   Title: Data Privacy Protection Policy
   Description: Comprehensive policy for citizen data privacy protection
   Stakeholders: Citizens, Government, Businesses
   Constitutional Principles: Privacy, Transparency, Accountability
   Priority: High
   ```

3. **Review Generated Policy**:
   - System will generate policy using AI synthesis
   - Review constitutional compliance score
   - Check stakeholder alignment metrics

4. **Approve and Deploy**:
   - Submit for formal verification
   - Review verification results
   - Deploy to blockchain if approved

## 🔄 Core Governance Workflows

### Workflow 1: Policy Creation and Validation

```mermaid
flowchart TD
    START([User Request]) --> AUTH{Authentication}
    AUTH -->|Valid| INPUT[Input Policy Details]
    AUTH -->|Invalid| LOGIN[Redirect to Login]
    
    INPUT --> SYNTH[AI Policy Synthesis]
    SYNTH --> CONST[Constitutional Validation]
    CONST --> VERIFY[Formal Verification]
    VERIFY --> APPROVE[Governance Approval]
    APPROVE --> DEPLOY[Blockchain Deployment]
    DEPLOY --> SUCCESS([Policy Active])
    
    LOGIN --> AUTH
```

**Step-by-Step Process**:

1. **Authentication** (2-3 seconds)
   - User provides credentials
   - System validates JWT token
   - RBAC permissions checked

2. **Policy Input** (30-60 seconds)
   - User fills policy creation form
   - System validates input parameters
   - Constitutional principles selected

3. **AI Synthesis** (5-10 seconds)
   - Multi-model consensus generation
   - Constitutional compliance scoring
   - Stakeholder alignment analysis

4. **Formal Verification** (10-30 seconds)
   - Z3 SMT solver validation
   - Safety property checking
   - Logical consistency verification

5. **Governance Approval** (Variable)
   - OPA policy enforcement
   - Constitutional council review
   - Stakeholder feedback integration

6. **Blockchain Deployment** (30-60 seconds)
   - Solana smart contract deployment
   - Immutable policy storage
   - Audit trail creation

### Workflow 2: Constitutional Amendment Process

**Prerequisites**:
- Constitutional Council membership
- Multi-signature approval (3 of 5 members)
- Formal verification passing

**Process**:
1. **Amendment Proposal**:
   ```bash
   curl -X POST http://localhost:8001/api/v1/constitutional/propose \
     -H "Authorization: Bearer $COUNCIL_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "amendment_type": "principle_addition",
       "title": "Digital Rights Amendment",
       "description": "Adding digital rights as fundamental constitutional principle",
       "proposed_changes": {
         "new_principles": ["digital_rights", "algorithmic_transparency"]
       }
     }'
   ```

2. **Multi-Signature Collection**:
   - Each council member signs the amendment
   - System validates signatures cryptographically
   - Requires 3 of 5 signatures for approval

3. **Constitutional Hash Update**:
   - New constitutional hash generated
   - All services updated with new hash
   - Cache invalidation across system

### Workflow 3: Emergency Policy Override

**Use Case**: Critical security threat requiring immediate policy changes

**Process**:
1. **Emergency Declaration**:
   ```bash
   curl -X POST http://localhost:8005/api/v1/emergency/declare \
     -H "Authorization: Bearer $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "threat_level": "critical",
       "description": "Active security breach detected",
       "override_policies": ["data_access_policy", "authentication_policy"],
       "duration_hours": 24
     }'
   ```

2. **Immediate Enforcement**:
   - OPA policies updated instantly
   - All services notified of changes
   - Emergency audit logging activated

3. **Post-Emergency Review**:
   - Constitutional compliance assessment
   - Stakeholder impact analysis
   - Permanent policy updates if needed

## 🧪 Interactive Examples

### Example 1: Testing Constitutional Compliance

```python
import httpx
import json

async def test_constitutional_compliance():
    """Test various policy scenarios for constitutional compliance."""
    
    test_policies = [
        {
            "name": "Privacy Policy",
            "content": "Citizens have the right to privacy and data protection",
            "expected_score": 0.9
        },
        {
            "name": "Surveillance Policy", 
            "content": "Government can monitor all citizen communications",
            "expected_score": 0.3
        },
        {
            "name": "Transparency Policy",
            "content": "All government decisions must be publicly documented",
            "expected_score": 0.95
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for policy in test_policies:
            response = await client.post(
                "http://localhost:8001/api/v1/constitutional/validate",
                json={"policy": policy["content"]}
            )
            
            result = response.json()
            score = result["compliance_score"]
            
            print(f"Policy: {policy['name']}")
            print(f"Compliance Score: {score:.2f}")
            print(f"Expected: {policy['expected_score']:.2f}")
            print(f"Status: {'✅ PASS' if score >= policy['expected_score'] else '❌ FAIL'}")
            print("-" * 50)

# Run the test
import asyncio
asyncio.run(test_constitutional_compliance())
```

### Example 2: Multi-Model Policy Generation

```python
async def generate_policy_with_consensus():
    """Generate policy using multi-model consensus."""
    
    policy_request = {
        "title": "AI Ethics Policy",
        "description": "Ethical guidelines for AI system deployment",
        "stakeholders": ["citizens", "developers", "government"],
        "constitutional_principles": ["transparency", "accountability", "fairness"],
        "domain": "technology",
        "priority": "high"
    }
    
    async with httpx.AsyncClient() as client:
        # Generate policy
        response = await client.post(
            "http://localhost:8004/api/v1/synthesis/generate",
            json=policy_request
        )
        
        result = response.json()
        
        print("Generated Policy:")
        print(f"Title: {result['policy']['title']}")
        print(f"Content: {result['policy']['content'][:200]}...")
        print(f"Constitutional Compliance: {result['synthesis_metadata']['constitutional_compliance']:.2f}")
        print(f"Consensus Score: {result['synthesis_metadata']['consensus_score']:.2f}")
        print(f"Models Used: {', '.join(result['synthesis_metadata']['models_used'])}")
        
        # Run consensus validation
        consensus_response = await client.post(
            "http://localhost:8004/api/v1/synthesis/consensus",
            json={
                "policy_content": result['policy']['content'],
                "models": ["qwen3-32b", "deepseek-chat", "qwen3-235b"],
                "consensus_threshold": 0.8
            }
        )
        
        consensus_result = consensus_response.json()
        print(f"\nConsensus Validation:")
        print(f"Overall Score: {consensus_result['consensus_result']['overall_score']:.2f}")
        print(f"Consensus Achieved: {consensus_result['consensus_result']['consensus_achieved']}")

# Run the example
asyncio.run(generate_policy_with_consensus())
```

## 🔧 Configuration and Customization

### Environment Configuration
```bash
# Core service configuration
export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
export DATABASE_URL="postgresql://user:pass@localhost:5432/acgs_db"
export REDIS_URL="redis://localhost:6379/0"

# Performance tuning
export MAX_CONCURRENT_REQUESTS=100
export CACHE_TTL_SECONDS=300
export RESPONSE_TIMEOUT_SECONDS=30

# Security settings
export JWT_SECRET_KEY="your-secure-secret-key"
export ENABLE_RATE_LIMITING=true
export MAX_REQUESTS_PER_MINUTE=1000
```

### Service-Specific Configuration
```yaml
# config/services/constitutional_ai_config.yaml
constitutional_ai:
  compliance_threshold: 0.8
  validation_timeout: 30
  cache_enabled: true
  models:
    primary: "constitutional_ai_v2"
    fallback: "constitutional_ai_v1"

# config/services/governance_synthesis_config.yaml
governance_synthesis:
  consensus_threshold: 0.8
  max_generation_time: 60
  models:
    - "qwen3-32b"
    - "deepseek-chat"
    - "qwen3-235b"
```

## 📚 Next Steps

### For Developers
1. **Explore API Documentation**: Visit http://localhost:8001/docs
2. **Review Architecture**: Read [docs/architecture/](../architecture/)
3. **Contribute**: Check [CONTRIBUTING.md](../../CONTRIBUTING.md)
4. **Join Community**: Participate in code reviews and discussions

### For Operators
1. **Production Deployment**: Follow [docs/deployment/](../deployment/)
2. **Monitoring Setup**: Configure [monitoring dashboards](../monitoring/)
3. **Security Hardening**: Implement [security procedures](../security/)
4. **Backup Strategy**: Set up [backup and recovery](../deployment/backup_strategy.md)

### For End-Users
1. **Advanced Tutorials**: Explore governance workflow tutorials
2. **Policy Templates**: Use pre-built policy templates
3. **Dashboard Customization**: Customize your governance dashboard
4. **Training Materials**: Access user training resources

## 🆘 Getting Help

- **Documentation**: Browse comprehensive docs in `/docs`
- **Health Checks**: Use `./scripts/comprehensive_health_check.py`
- **Troubleshooting**: See [troubleshooting guide](../troubleshooting.md)
- **Community**: Join discussions and ask questions
- **Support**: Contact the ACGS-1 development team

---

**Welcome to ACGS-1!** You're now ready to start building constitutional governance systems. 🎉
