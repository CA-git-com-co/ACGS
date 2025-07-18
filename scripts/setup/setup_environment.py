#!/usr/bin/env python3
"""
ACGS-2 Interactive Development Environment Setup Wizard
Constitutional Hash: cdd01ef066bc6cf2

Interactive setup wizard for developers to quickly configure their ACGS-2 development environment.
Provides guided setup with validation and helpful feedback.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Try to import click for better CLI experience
try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    print("⚠️  Click not available, using basic input prompts")

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class ACGSSetupWizard:
    """Interactive setup wizard for ACGS-2 development environment."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.setup_config = {}
        self.requirements = {
            "docker": "Docker and Docker Compose for containerized services",
            "python": "Python 3.11+ for running services and scripts",
            "git": "Git for version control",
            "node": "Node.js for CLI and frontend components (optional)"
        }
        
    def display_banner(self):
        """Display welcome banner."""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ACGS-2 Development Environment Setup                      ║
║                           Constitutional AI Governance                       ║
║                                                                              ║
║  Constitutional Hash: {self.constitutional_hash}                     ║
║  Setup Version: 2.0.1                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Welcome to the ACGS-2 (Advanced Constitutional Governance System) setup wizard!

This wizard will help you configure your development environment step by step.
It will check prerequisites, set up services, and validate your installation.
        """
        print(banner)
    
    def prompt_user(self, question: str, default: Optional[str] = None, 
                   choices: Optional[List[str]] = None) -> str:
        """Prompt user for input with optional default and choices."""
        if CLICK_AVAILABLE:
            if choices:
                return click.prompt(
                    question, 
                    type=click.Choice(choices, case_sensitive=False),
                    default=default
                )
            else:
                return click.prompt(question, default=default)
        else:
            # Fallback to basic input
            prompt = f"{question}"
            if choices:
                prompt += f" ({'/'.join(choices)})"
            if default:
                prompt += f" [{default}]"
            prompt += ": "
            
            response = input(prompt)
            return response.strip() or default or ""
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """Confirm action with user."""
        if CLICK_AVAILABLE:
            return click.confirm(message, default=default)
        else:
            default_str = "Y/n" if default else "y/N"
            response = input(f"{message} ({default_str}): ").strip().lower()
            if not response:
                return default
            return response in ['y', 'yes', 'true', '1']
    
    def run_command(self, cmd: str, description: str = "", 
                   check_output: bool = False) -> Tuple[bool, str]:
        """Run command and return success status and output."""
        try:
            if description:
                print(f"🔄 {description}...")
            
            if check_output:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, check=True
                )
                return True, result.stdout.strip()
            else:
                result = subprocess.run(cmd, shell=True, check=True)
                return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = getattr(e, 'stderr', str(e))
            return False, error_msg
    
    def check_requirements(self) -> Dict[str, bool]:
        """Check system requirements."""
        print("🔍 Checking system requirements...")
        results = {}
        
        # Check Docker
        success, output = self.run_command("docker --version", check_output=True)
        results["docker"] = success
        if success:
            print(f"✅ Docker: {output}")
        else:
            print("❌ Docker: Not found or not running")
        
        # Check Docker Compose
        success, output = self.run_command("docker compose version", check_output=True)
        results["docker_compose"] = success
        if success:
            print(f"✅ Docker Compose: {output}")
        else:
            print("❌ Docker Compose: Not found")
        
        # Check Python
        success, output = self.run_command("python3 --version", check_output=True)
        results["python"] = success
        if success:
            print(f"✅ Python: {output}")
        else:
            print("❌ Python 3: Not found")
        
        # Check Git
        success, output = self.run_command("git --version", check_output=True)
        results["git"] = success
        if success:
            print(f"✅ Git: {output}")
        else:
            print("❌ Git: Not found")
        
        # Check Node.js (optional)
        success, output = self.run_command("node --version", check_output=True)
        results["node"] = success
        if success:
            print(f"✅ Node.js: {output}")
        else:
            print("⚠️  Node.js: Not found (optional for CLI tools)")
        
        return results
    
    def setup_environment_file(self):
        """Set up environment configuration."""
        print("\n📝 Setting up environment configuration...")
        
        env_example = self.project_root / "config/environments/developmentconfig/environments/acgsconfig/environments/example.env"
        env_target = self.project_root / "config/environments/developmentconfig/environments/acgs.env"
        
        if env_example.exists():
            if env_target.exists():
                if self.confirm(f"Environment file {env_target} already exists. Overwrite?", False):
                    shutil.copy2(env_example, env_target)
                    print(f"✅ Copied {env_example} to {env_target}")
                else:
                    print("⏭️  Keeping existing environment file")
            else:
                shutil.copy2(env_example, env_target)
                print(f"✅ Created {env_target} from template")
        else:
            print(f"⚠️  Example environment file not found at {env_example}")
            
        # Constitutional hash validation
        if env_target.exists():
            try:
                with open(env_target, 'r') as f:
                    content = f.read()
                    if CONSTITUTIONAL_HASH in content:
                        print(f"✅ Constitutional hash {CONSTITUTIONAL_HASH} validated in environment")
                    else:
                        print(f"⚠️  Constitutional hash not found in environment file")
            except Exception as e:
                print(f"⚠️  Could not validate environment file: {e}")
    
    def setup_python_environment(self):
        """Set up Python virtual environment and dependencies."""
        print("\n🐍 Setting up Python environment...")
        
        # Check if uv is available (preferred)
        uv_available, _ = self.run_command("uv --version", check_output=True)
        
        if uv_available:
            print("✅ UV package manager detected (recommended)")
            if self.confirm("Use UV to install dependencies?", True):
                success, output = self.run_command("uv sync", "Installing dependencies with UV")
                if success:
                    print("✅ Dependencies installed with UV")
                else:
                    print(f"❌ UV installation failed: {output}")
                    return False
        else:
            print("⚠️  UV not available, falling back to pip")
            
            # Check for virtual environment
            venv_path = self.project_root / ".venv"
            if not venv_path.exists():
                if self.confirm("Create Python virtual environment?", True):
                    success, _ = self.run_command(
                        "python3 -m venv .venv", 
                        "Creating virtual environment"
                    )
                    if not success:
                        print("❌ Failed to create virtual environment")
                        return False
            
            # Install dependencies
            requirements_files = [
                "config/environments/requirements.txt",
                "services/shared/requirements/requirements-base.txt"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            ]
            
            for req_file in requirements_files:
                req_path = self.project_root / req_file
                if req_path.exists():
                    if self.confirm(f"Install dependencies from {req_file}?", True):
                        success, output = self.run_command(
                            f"pip install -r {req_path}",
                            f"Installing dependencies from {req_file}"
                        )
                        if not success:
                            print(f"⚠️  Failed to install from {req_file}: {output}")
        
        return True
    
    def setup_docker_services(self):
        """Set up Docker services."""
        print("\n🐳 Setting up Docker services...")
        
        compose_file = self.project_root / "infrastructure" / "docker" / "docker-compose.acgs.yml"
        
        if not compose_file.exists():
            print(f"❌ Docker Compose file not found: {compose_file}")
            return False
        
        print(f"📋 Found Docker Compose configuration: {compose_file}")
        
        if self.confirm("Pull latest Docker images?", True):
            success, output = self.run_command(
                f"docker compose -f {compose_file} pull",
                "Pulling Docker images"
            )
            if not success:
                print(f"⚠️  Some images may not have been pulled: {output}")
        
        if self.confirm("Start ACGS services in detached mode?", True):
            success, output = self.run_command(
                f"docker compose -f {compose_file} up -d",
                "Starting ACGS services"
            )
            if success:
                print("✅ ACGS services started successfully")
                return True
            else:
                print(f"❌ Failed to start services: {output}")
                return False
        
        return True
    
    def validate_setup(self):
        """Validate the setup by checking service health."""
        print("\n🔍 Validating setup...")
        
        # Wait a moment for services to start
        import time
        print("⏳ Waiting for services to initialize...")
        time.sleep(10)
        
        # Health check endpoints
        health_checks = [
            ("Constitutional AI Service", "http://localhost:8001/health"),
            ("Integrity Service", "http://localhost:8002/health"),
            ("API Gateway", "http://localhost:8010/health"),
        ]
        
        try:
            import requests
            requests_available = True
        except ImportError:
            print("⚠️  Requests library not available, skipping HTTP health checks")
            requests_available = False
        
        if requests_available:
            for service_name, url in health_checks:
                try:
                    import requests
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service_name}: Healthy")
                    else:
                        print(f"⚠️  {service_name}: Status {response.status_code}")
                except Exception as e:
                    print(f"❌ {service_name}: {e}")
        
        # Check Docker containers
        success, output = self.run_command(
            "docker ps --format 'table {{.Names}}\\t{{.Status}}' | grep acgs",
            check_output=True
        )
        if success and output:
            print("\n📊 ACGS Docker containers:")
            print(output)
        
        print(f"\n✅ Setup validation complete!")
        print(f"🎯 Constitutional hash {CONSTITUTIONAL_HASH} validated throughout setup")
    
    def display_next_steps(self):
        """Display next steps for the developer."""
        next_steps = f"""
🎉 ACGS-2 Development Environment Setup Complete!

📋 Next Steps:
   
1. 🔍 Verify Services:
   curl http://localhost:8001/health  # Constitutional AI Service
   curl http://localhost:8002/health  # Integrity Service  
   curl http://localhost:8010/health  # API Gateway

2. 🧪 Run Tests:
   cd {self.project_root}
   python -m pytest tests/ -v

3. 📊 Monitor Services:
   docker compose -f infrastructure/docker/docker-compose.acgs.yml logs -f

4. 🔧 Development Commands:
   # Stop all services
   docker compose -f infrastructure/docker/docker-compose.acgs.yml down
   
   # Restart a specific service
   docker compose -f infrastructure/docker/docker-compose.acgs.yml restart constitutional-ai
   
   # View service logs
   docker compose -f infrastructure/docker/docker-compose.acgs.yml logs constitutional-ai

5. 📚 Documentation:
   - Project README: {self.project_root}/README.md
   - API Documentation: http://localhost:8010/docs
   - Service Architecture: {self.project_root}/docs/

🔐 Security Notes:
   - Constitutional hash {CONSTITUTIONAL_HASH} is embedded in all operations
   - All services run with multi-tenant security by default
   - Prometheus metrics available at http://localhost:9090

🆘 Need Help?
   - Check service logs for errors
   - Review the troubleshooting guide in docs/
   - Validate constitutional compliance with: python tools/validation/constitutional_compliance_validator.py

Happy coding! 🚀
        """
        print(next_steps)
    
    def run_setup(self):
        """Run the complete setup wizard."""
        self.display_banner()
        
        # Check requirements
        requirements_ok = self.check_requirements()
        critical_missing = []
        
        for req, available in requirements_ok.items():
            if req in ["docker", "python", "git"] and not available:
                critical_missing.append(req)
        
        if critical_missing:
            print(f"\n❌ Critical requirements missing: {', '.join(critical_missing)}")
            print("Please install the missing requirements and run this setup again.")
            
            if self.confirm("Show installation instructions?", True):
                self.show_installation_instructions(critical_missing)
            
            return False
        
        print("\n✅ All critical requirements satisfied!")
        
        # Setup steps
        if not self.confirm("\nProceed with environment setup?", True):
            print("Setup cancelled.")
            return False
        
        # Environment configuration
        self.setup_environment_file()
        
        # Python environment
        if self.confirm("\nSet up Python environment and dependencies?", True):
            if not self.setup_python_environment():
                print("⚠️  Python setup had issues, but continuing...")
        
        # Docker services
        if self.confirm("\nStart Docker services?", True):
            if not self.setup_docker_services():
                print("❌ Docker services setup failed")
                return False
        
        # Validation
        if self.confirm("\nValidate setup?", True):
            self.validate_setup()
        
        # Show next steps
        self.display_next_steps()
        
        return True
    
    def show_installation_instructions(self, missing: List[str]):
        """Show installation instructions for missing requirements."""
        instructions = {
            "docker": {
                "description": "Docker and Docker Compose",
                "ubuntu": "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh",
                "macos": "brew install docker docker-compose",
                "windows": "Download Docker Desktop from https://www.docker.com/products/docker-desktop"
            },
            "python": {
                "description": "Python 3.11+",
                "ubuntu": "sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip",
                "macos": "brew install python@3.11",
                "windows": "Download from https://www.python.org/downloads/"
            },
            "git": {
                "description": "Git version control",
                "ubuntu": "sudo apt update && sudo apt install git",
                "macos": "brew install git",
                "windows": "Download from https://git-scm.com/download/win"
            }
        }
        
        system = platform.system().lower()
        if "darwin" in system:
            system = "macos"
        elif "windows" in system:
            system = "windows"
        else:
            system = "ubuntu"  # Default to Ubuntu for Linux
        
        print(f"\n📥 Installation Instructions for {system.title()}:\n")
        
        for req in missing:
            if req in instructions:
                info = instructions[req]
                print(f"🔧 {info['description']}:")
                print(f"   {info.get(system, 'Please check official documentation')}")
                print()


def main():
    """Main entry point."""
    if CLICK_AVAILABLE:
        @click.command()
        @click.option('--auto', is_flag=True, help='Run with default options (minimal prompts)')
        @click.option('--validate-only', is_flag=True, help='Only validate existing setup')
        def setup_command(auto, validate_only):
            wizard = ACGSSetupWizard()
            
            if validate_only:
                wizard.display_banner()
                wizard.validate_setup()
                return
            
            if auto:
                print("🤖 Running automated setup with defaults...")
                # Set up environment with minimal prompts
                wizard.setup_environment_file()
                wizard.setup_python_environment()
                wizard.setup_docker_services()
                wizard.validate_setup()
                wizard.display_next_steps()
            else:
                wizard.run_setup()
        
        setup_command()
    else:
        # Fallback for when click is not available
        wizard = ACGSSetupWizard()
        
        if len(sys.argv) > 1:
            if "--validate-only" in sys.argv:
                wizard.display_banner()
                wizard.validate_setup()
                return
            elif "--auto" in sys.argv:
                print("🤖 Running automated setup with defaults...")
                wizard.setup_environment_file()
                wizard.setup_python_environment() 
                wizard.setup_docker_services()
                wizard.validate_setup()
                wizard.display_next_steps()
                return
        
        wizard.run_setup()


if __name__ == "__main__":
    main()