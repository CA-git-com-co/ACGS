#!/usr/bin/env python3
"""
ACGS-2 Local Services Runner
Constitutional Hash: cdd01ef066bc6cf2

Run ACGS-2 services directly without Docker when authentication issues occur.
"""

import asyncio
import subprocess
import os
import sys
import signal
import time
from pathlib import Path
from typing import List, Dict, Any

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service configurations
SERVICES = {
    "constitutional_core": {
        "path": "services/core/constitutional-ai",
        "port": 8001,
        "env": {
            "SERVICE_NAME": "constitutional-core",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "DATABASE_URL": "postgresql://acgs_user:acgs_password@localhost:5439/acgs_db",
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "groqcloud_policy": {
        "path": "services/core/groqcloud-policy-integration",
        "port": 8023,
        "env": {
            "SERVICE_NAME": "groqcloud-policy",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "USE_GROQ": "false",
            "KIMI_K2_ENABLED": "true"
        }
    },
    "multi_agent_coordination": {
        "path": "services/core/multi-agent-coordination",
        "port": 8008,
        "env": {
            "SERVICE_NAME": "multi-agent-coordination",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "worker_agents": {
        "path": "services/core/worker-agents",
        "port": 8009,
        "env": {
            "SERVICE_NAME": "worker-agents",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "blackboard_coordination": {
        "path": "services/core/blackboard-coordination",
        "port": 8010,
        "env": {
            "SERVICE_NAME": "blackboard-coordination",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "mcp_aggregator": {
        "path": "services/mcp/aggregator",
        "port": 3000,
        "env": {
            "SERVICE_NAME": "mcp-aggregator",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "a2a_policy": {
        "path": "services/core/a2a-policy-integration",
        "port": 8020,
        "env": {
            "SERVICE_NAME": "a2a-policy",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "JWT_SECRET": "acgs_jwt_secret",
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "security_validation": {
        "path": "services/core/security-validation",
        "port": 8021,
        "env": {
            "SERVICE_NAME": "security-validation",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "ML_MODELS_PATH": "./models"
        }
    },
    "consensus_engine": {
        "path": "services/core/consensus-engine",
        "port": 8011,
        "env": {
            "SERVICE_NAME": "consensus-engine",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "REDIS_URL": "redis://localhost:6389/0"
        }
    },
    "human_in_the_loop": {
        "path": "services/core/human-in-the-loop",
        "port": 8012,
        "env": {
            "SERVICE_NAME": "human-in-the-loop",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH
        }
    },
    "auth_service": {
        "path": "services/core/auth-service",
        "port": 8013,
        "env": {
            "SERVICE_NAME": "auth-service",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "JWT_SECRET": "acgs_jwt_secret_key"
        }
    },
    "monitoring_service": {
        "path": "services/core/monitoring-service",
        "port": 8014,
        "env": {
            "SERVICE_NAME": "monitoring-service",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH
        }
    },
    "audit_service": {
        "path": "services/core/audit-service",
        "port": 8015,
        "env": {
            "SERVICE_NAME": "audit-service",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH
        }
    },
    "api_gateway": {
        "path": "services/core/api-gateway",
        "port": 8080,
        "env": {
            "SERVICE_NAME": "api-gateway",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH,
            "JWT_SECRET": "acgs_jwt_secret_key"
        }
    },
    "gdpr_compliance": {
        "path": "services/core/gdpr-compliance",
        "port": 8016,
        "env": {
            "SERVICE_NAME": "gdpr-compliance",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH
        }
    },
    "alerting_service": {
        "path": "services/core/alerting-service",
        "port": 8017,
        "env": {
            "SERVICE_NAME": "alerting-service",
            "CONSTITUTIONAL_HASH": CONSTITUTIONAL_HASH
        }
    }
}

class ServiceManager:
    """Manage local service processes"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
    def start_service(self, name: str, config: Dict[str, Any]) -> bool:
        """Start a single service"""
        service_path = Path(config["path"])
        if not service_path.exists():
            print(f"❌ Service path not found: {service_path}")
            return False
        
        # Set up environment
        env = os.environ.copy()
        env.update(config["env"])
        env["PORT"] = str(config["port"])
        
        # Create command
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(config["port"]),
            "--reload"
        ]
        
        try:
            print(f"🚀 Starting {name} on port {config['port']}...")
            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes[name] = process
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if still running
            if process.poll() is None:
                print(f"✅ {name} started successfully")
                return True
            else:
                print(f"❌ {name} failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {name}: {e}")
            return False
    
    def start_infrastructure(self):
        """Start infrastructure services (Redis, PostgreSQL)"""
        print("🔧 Starting infrastructure services...")
        
        # Check if Redis is running
        try:
            subprocess.run(["redis-cli", "-p", "6389", "ping"], 
                         capture_output=True, check=True)
            print("✅ Redis already running")
        except:
            print("⚠️ Redis not running. Please start Redis on port 6389")
            print("   Run: redis-server --port 6389")
        
        # Check if PostgreSQL is running
        try:
            subprocess.run(["pg_isready", "-p", "5439"], 
                         capture_output=True, check=True)
            print("✅ PostgreSQL already running")
        except:
            print("⚠️ PostgreSQL not running. Please start PostgreSQL on port 5439")
    
    def start_all(self):
        """Start all services"""
        print(f"🚀 Starting ACGS-2 Services Locally")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)
        
        # Start infrastructure first
        self.start_infrastructure()
        print()
        
        # Start each service
        self.running = True
        success_count = 0
        
        for name, config in SERVICES.items():
            if self.start_service(name, config):
                success_count += 1
            time.sleep(1)  # Stagger starts
        
        print()
        print(f"📊 Started {success_count}/{len(SERVICES)} services")
        
        if success_count > 0:
            print("\n🔍 Check service health:")
            for name, config in SERVICES.items():
                if name in self.processes:
                    print(f"   curl http://localhost:{config['port']}/health")
            
            print("\n⌨️  Press Ctrl+C to stop all services")
            
            # Keep running
            try:
                while self.running:
                    time.sleep(1)
                    # Check if processes are still alive
                    for name, process in list(self.processes.items()):
                        if process.poll() is not None:
                            print(f"⚠️ {name} stopped unexpectedly")
                            del self.processes[name]
            except KeyboardInterrupt:
                print("\n🛑 Stopping services...")
                self.stop_all()
        else:
            print("❌ No services started successfully")
    
    def stop_all(self):
        """Stop all running services"""
        self.running = False
        for name, process in self.processes.items():
            print(f"🛑 Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        self.processes.clear()
        print("✅ All services stopped")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    
    # Check if uvicorn is available
    try:
        import uvicorn
        print("✅ uvicorn installed")
    except ImportError:
        print("❌ uvicorn not installed. Run: pip install uvicorn[standard]")
        return False
    
    # Check if FastAPI is available
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("❌ FastAPI not installed. Run: pip install fastapi")
        return False
    
    return True

def main():
    """Main entry point"""
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install required packages.")
        sys.exit(1)
    
    manager = ServiceManager()
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal")
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start services
    manager.start_all()

if __name__ == "__main__":
    main()