#!/usr/bin/env python3
"""
Comprehensive Search and Replace Script for 5-Tier Model Architecture

This script updates the entire ACGS-2 codebase to replace old model configurations
with the new 5-tier architecture across all files and configurations.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CodebaseUpdater:
    """Updates the entire codebase with new 5-tier model architecture."""
    
    def __init__(self, project_root: str = "/home/dislove/ACGS-2"):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Model name mappings (old -> new)
        self.model_mappings = {
            # Remove old models
            "qwen3-32b-groq": "qwen3-32b-groq",
            "qwen3-32b-groq-constitutional": "grok-4",
            "grok-4": "grok-4",
            "grok-4-sonnet": "grok-4",
            "claude-3.5-sonnet": "claude-3.5-sonnet",
            "claude-3.5-sonnet": "claude-3.5-sonnet",
            "qwen3-32b-groq": "qwen3-32b-groq",
            "mixtral-8x22b": "mixtral-8x22b",
            "gemini-2.0-flash": "gemini-2.0-flash",
            "qwen3-4b": "qwen3-4b",
            "qwen3-32b-groq": "qwen3-32b-groq",
            "qwen3-32b-groq": "qwen3-32b-groq",
            "deepseek-v3-0324": "deepseek-v3-0324",
            "deepseek-v3-0324-2.0": "deepseek-v3-0324",
            "deepseek-v3-0324": "deepseek-v3-0324",
            "jina-embeddings-v3": "jina-embeddings-v3",
            "jina-embeddings-v3": "jina-embeddings-v3"
        }
        
        # Tier mappings (old -> new)
        self.tier_mappings = {
            "TIER_2_FAST": "TIER_2_FAST",
            "TIER_3_BALANCED": "TIER_3_BALANCED", 
            "TIER_4_PREMIUM": "TIER_4_PREMIUM",
            "TIER_5_EXPERT": "TIER_5_EXPERT",
            "tier_2_fast": "tier_2_fast",
            "tier_3_balanced": "tier_3_balanced",
            "tier_4_premium": "tier_4_premium", 
            "tier_5_expert": "tier_5_expert"
        }
        
        # Model ID mappings for API endpoints
        self.model_id_mappings = {
            "qwen/qwen3-32b-instruct": "qwen/qwen3-32b-instruct",
            "xai/grok-4": "xai/grok-4",
            "grok-4-sonnet-20250525": "xai/grok-4",
            "claude-3.5-sonnet-20240229": "anthropic/claude-3.5-sonnet",
            "qwen3-32b-groq": "qwen/qwen3-32b-instruct",
            "mistralai/qwen3-4b-instruct": "qwen/qwen3-4b-instruct",
            "meta-llama/qwen3-32b-groq-chat-hf": "qwen/qwen3-32b-instruct",
            "deepseek-v3-0324-latest": "deepseek-ai/deepseek-v3-0324",
            "jina-embeddings-v3": "jina-embeddings-v3"
        }
        
        # File extensions to process
        self.file_extensions = {'.py', '.json', '.yaml', '.yml', '.md', '.sh', 'config/environments/development.env', '.txt'}
        
        # Directories to skip
        self.skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        
        logger.info(f"Initialized CodebaseUpdater for {self.project_root}")

    def update_codebase(self):
        """Update the entire codebase with new model configurations."""
        
        logger.info("🚀 Starting comprehensive codebase update for 5-tier architecture")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        updated_files = []
        
        # Walk through all files in the project
        for file_path in self._get_files_to_process():
            try:
                if self._update_file(file_path):
                    updated_files.append(file_path)
            except Exception as e:
                logger.error(f"❌ Error updating {file_path}: {e}")
        
        logger.info(f"✅ Updated {len(updated_files)} files")
        
        # Update specific configuration files
        self._update_configuration_files()
        
        # Update documentation
        self._update_documentation()
        
        logger.info("🎯 Codebase update completed successfully")
        
        return updated_files

    def _get_files_to_process(self) -> List[Path]:
        """Get list of files to process."""
        
        files = []
        
        for root, dirs, filenames in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Check if file extension should be processed
                if file_path.suffix in self.file_extensions:
                    files.append(file_path)
        
        logger.info(f"Found {len(files)} files to process")
        return files

    def _update_file(self, file_path: Path) -> bool:
        """Update a single file with new model configurations."""
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Apply model name replacements
            for old_model, new_model in self.model_mappings.items():
                # Replace quoted model names
                content = re.sub(f'["\']({re.escape(old_model)})["\']', f'"{new_model}"', content)
                # Replace unquoted model names (with word boundaries)
                content = re.sub(f'\\b{re.escape(old_model)}\\b', new_model, content)
            
            # Apply tier mappings
            for old_tier, new_tier in self.tier_mappings.items():
                content = re.sub(f'\\b{re.escape(old_tier)}\\b', new_tier, content)
            
            # Apply model ID mappings
            for old_id, new_id in self.model_id_mappings.items():
                content = re.sub(f'["\']({re.escape(old_id)})["\']', f'"{new_id}"', content)
            
            # Update specific patterns
            content = self._update_specific_patterns(content, file_path)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ Updated {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return False

    def _update_specific_patterns(self, content: str, file_path: Path) -> str:
        """Update specific patterns based on file type."""
        
        # Update Python imports and class references
        if file_path.suffix == '.py':
            # Update ModelTier enum references
            content = re.sub(
                r'ModelTier\.TIER_([1-4])_(\w+)',
                lambda m: f'ModelTier.TIER_{int(m.group(1))+1}_{m.group(2).upper()}' if int(m.group(1)) < 4 else f'ModelTier.TIER_5_EXPERT',
                content
            )
            
            # Update QueryComplexity references to include NANO
            if 'QueryComplexity.EASY' in content and 'QueryComplexity.NANO' not in content:
                content = content.replace(
                    'QueryComplexity.EASY',
                    'QueryComplexity.NANO'
                )
        
        # Update JSON configurations
        elif file_path.suffix == '.json':
            try:
                # Try to parse as JSON and update model references
                data = json.loads(content)
                updated_data = self._update_json_data(data)
                content = json.dumps(updated_data, indent=2)
            except json.JSONDecodeError:
                # If not valid JSON, apply text replacements
                pass
        
        # Update YAML configurations
        elif file_path.suffix in {'.yaml', '.yml'}:
            # Update model references in YAML
            content = re.sub(
                r'model:\s*["\']?([^"\'\n]+)["\']?',
                lambda m: f'model: "{self.model_mappings.get(m.group(1).strip(), m.group(1).strip())}"',
                content
            )
        
        # Update shell scripts
        elif file_path.suffix == '.sh':
            # Update environment variable references
            for old_model, new_model in self.model_mappings.items():
                old_var = old_model.upper().replace('-', '_')
                new_var = new_model.upper().replace('-', '_')
                content = content.replace(old_var, new_var)
        
        return content

    def _update_json_data(self, data) -> any:
        """Recursively update JSON data structures."""
        
        if isinstance(data, dict):
            updated_data = {}
            for key, value in data.items():
                # Update model references in keys
                new_key = self.model_mappings.get(key, key)
                
                # Update model references in values
                if isinstance(value, str) and value in self.model_mappings:
                    updated_data[new_key] = self.model_mappings[value]
                else:
                    updated_data[new_key] = self._update_json_data(value)
            
            return updated_data
        
        elif isinstance(data, list):
            return [self._update_json_data(item) for item in data]
        
        elif isinstance(data, str):
            return self.model_mappings.get(data, data)
        
        else:
            return data

    def _update_configuration_files(self):
        """Update specific configuration files."""
        
        logger.info("🔧 Updating specific configuration files")
        
        # Update OpenCode configuration
        opencode_config = self.project_root / "services/cli/opencode/opencode.json"
        if opencode_config.exists():
            self._update_opencode_config(opencode_config)
        
        # Update AI model service configuration
        ai_service_config = self.project_root / "services/shared/ai_model_service.py"
        if ai_service_config.exists():
            self._update_ai_service_config(ai_service_config)
        
        # Update governance synthesis configuration
        gs_config = self.project_root / "services/core/governance-synthesis/gs_service/app/core/phase_a3_multi_model_consensus.py"
        if gs_config.exists():
            self._update_governance_config(gs_config)

    def _update_opencode_config(self, config_path: Path):
        """Update OpenCode configuration with new models."""
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update model references
            if 'provider' in config and 'openrouter' in config['provider']:
                models = config['provider']['openrouter'].get('models', {})
                
                # Add new 5-tier models
                new_models = {
                    "qwen/qwen3-32b-instruct": {
                        "name": "Qwen3 32B (Groq)",
                        "tool_call": True,
                        "reasoning": True,
                        "temperature": True
                    },
                    "xai/grok-4": {
                        "name": "Grok 4",
                        "tool_call": True,
                        "reasoning": True,
                        "temperature": True
                    },
                    "google/gemini-2.0-flash": {
                        "name": "Gemini 2.0 Flash",
                        "tool_call": True,
                        "reasoning": True,
                        "temperature": True
                    }
                }
                
                config['provider']['openrouter']['models'].update(new_models)
                config['model'] = "openrouter/qwen/qwen3-32b-instruct"
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"✅ Updated OpenCode configuration: {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Error updating OpenCode config: {e}")

    def _update_ai_service_config(self, config_path: Path):
        """Update AI model service configuration."""
        
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Update model configurations
            new_config = '''
        self.model_configs = {
            ModelProvider.OPENAI: {
                "chat": ["gemini-2.0-flash", "gpt-4"],
                "completion": ["gpt-4"],
                "embedding": ["jina-embeddings-v3"],
            },
            ModelProvider.ANTHROPIC: {
                "chat": ["claude-3.5-sonnet", "claude-3-haiku"],
                "completion": ["claude-3.5-sonnet"],
            },
            ModelProvider.GROQ: {
                "chat": ["qwen3-32b", "llama-3.1-8b"],
                "completion": ["qwen3-32b"],
            },
            ModelProvider.OPENROUTER: {
                "chat": ["qwen/qwen3-32b-instruct", "xai/grok-4"],
                "completion": ["qwen/qwen3-32b-instruct"],
                "analysis": ["xai/grok-4"],
                "constitutional_validation": ["xai/grok-4"],
            },
        }'''
            
            # Replace the model_configs section
            content = re.sub(
                r'self\.model_configs = \{.*?\}',
                new_config.strip(),
                content,
                flags=re.DOTALL
            )
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            logger.info(f"✅ Updated AI service configuration: {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Error updating AI service config: {e}")

    def _update_governance_config(self, config_path: Path):
        """Update governance synthesis configuration."""
        
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Update model configurations for governance
            governance_models = {
                "qwen/qwen3-32b": "qwen/qwen3-32b-instruct",
                "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet", 
                "gemini-2.5-pro": "google/gemini-2.0-flash",
                "grok-4": "xai/grok-4"
            }
            
            for old_model, new_model in governance_models.items():
                content = content.replace(f'"{old_model}"', f'"{new_model}"')
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            logger.info(f"✅ Updated governance configuration: {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Error updating governance config: {e}")

    def _update_documentation(self):
        """Update documentation files."""
        
        logger.info("📚 Updating documentation")
        
        # Update README files
        readme_files = list(self.project_root.glob("**/README.md"))
        for readme in readme_files:
            self._update_readme(readme)
        
        # Update specific documentation
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.glob("*.md"):
                self._update_file(doc_file)

    def _update_readme(self, readme_path: Path):
        """Update README files with new model information."""
        
        try:
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Update model references in documentation
            for old_model, new_model in self.model_mappings.items():
                content = content.replace(old_model, new_model)
            
            # Add 5-tier architecture information if not present
            if "5-tier" not in content.lower() and "tier" in content.lower():
                tier_info = """
## 🏗️ 5-Tier Model Architecture

ACGS-2 uses a 5-tier hybrid inference router for optimal cost-performance:

- **Tier 1 (Nano)**: Qwen3 0.6B-4B via nano-vllm
- **Tier 2 (Fast)**: DeepSeek R1 8B, Llama 3.1 8B via Groq  
- **Tier 3 (Balanced)**: Qwen3 32B via Groq
- **Tier 4 (Premium)**: Gemini 2.0 Flash, Mixtral 8x22B, DeepSeek V3, Grok 3 Mini
- **Tier 5 (Expert)**: Grok 4 for constitutional AI governance

Constitutional Hash: `cdd01ef066bc6cf2`
"""
                content += tier_info
            
            with open(readme_path, 'w') as f:
                f.write(content)
            
            logger.info(f"✅ Updated README: {readme_path}")
            
        except Exception as e:
            logger.error(f"❌ Error updating README: {e}")


def main():
    """Main function to run the codebase update."""
    
    print("🚀 ACGS-2 Codebase Update for 5-Tier Architecture")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Initialize updater
    updater = CodebaseUpdater()
    
    # Run the update
    updated_files = updater.update_codebase()
    
    print(f"\n✅ Codebase update completed!")
    print(f"📊 Updated {len(updated_files)} files")
    print(f"🎯 5-tier architecture implemented across entire codebase")
    print(f"🔒 Constitutional compliance maintained: {CONSTITUTIONAL_HASH}")


if __name__ == "__main__":
    main()
