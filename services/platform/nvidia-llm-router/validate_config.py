#!/usr/bin/env python3
"""
Configuration Validation Script for NVIDIA LLM Router

Validates the routing configuration file for syntax and logical consistency.
"""

import os
import sys

import yaml


def validate_config_file(config_path: str) -> bool:
    """
    Validate the router configuration file

    Args:
        config_path: Path to the configuration file

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        with open(config_path) as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return False
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False

    errors = []
    warnings = []

    # Validate global section
    if "global" not in config:
        errors.append("Missing 'global' section")
    else:
        global_config = config["global"]
        if "version" not in global_config:
            warnings.append("Missing version in global config")

    # Validate models section
    if "models" not in config:
        errors.append("Missing 'models' section")
    else:
        models_config = config["models"]
        required_tiers = ["efficient", "standard", "premium"]

        for tier in required_tiers:
            if tier not in models_config:
                warnings.append(f"Missing model tier: {tier}")
            else:
                tier_models = models_config[tier]
                if not isinstance(tier_models, list):
                    errors.append(f"Model tier '{tier}' must be a list")
                else:
                    for i, model in enumerate(tier_models):
                        if not isinstance(model, dict):
                            errors.append(
                                f"Model {i} in tier '{tier}' must be a dictionary"
                            )
                            continue

                        if "name" not in model:
                            errors.append(f"Model {i} in tier '{tier}' missing 'name'")

                        if "capabilities" not in model:
                            warnings.append(
                                f"Model {i} in tier '{tier}' missing 'capabilities'"
                            )

    # Validate task routing
    if "task_routing" not in config:
        warnings.append("Missing 'task_routing' section")
    else:
        task_routing = config["task_routing"]
        required_tasks = list(task_routing.keys())

        for task in required_tasks:
            if task not in task_routing:
                warnings.append(f"Missing task routing for: {task}")
            else:
                task_config = task_routing[task]
                if "preferred_models" not in task_config:
                    errors.append(f"Task '{task}' missing 'preferred_models'")
                if "fallback_models" not in task_config:
                    warnings.append(f"Task '{task}' missing 'fallback_models'")

    # Validate complexity routing
    if "complexity_routing" not in config:
        warnings.append("Missing 'complexity_routing' section")
    else:
        complexity_routing = config["complexity_routing"]
        required_levels = ["low", "medium", "high"]

        for level in required_levels:
            if level not in complexity_routing:
                warnings.append(f"Missing complexity level: {level}")
            else:
                level_config = complexity_routing[level]
                if "preferred_tier" not in level_config:
                    errors.append(
                        f"Complexity level '{level}' missing 'preferred_tier'"
                    )

    # Validate ACGS integration
    if "acgs_integration" not in config:
        warnings.append("Missing 'acgs_integration' section")
    else:
        acgs_config = config["acgs_integration"]
        if "enable_constitutional_routing" not in acgs_config:
            warnings.append("Missing 'enable_constitutional_routing' setting")

    # Print results
    print(f"📋 Configuration Validation Results for: {config_path}")
    print("=" * 60)

    if errors:
        print("❌ ERRORS:")
        for error in errors:
            print(f"   • {error}")
        print()

    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    if not errors and not warnings:
        print("✅ Configuration is valid with no issues!")
    elif not errors:
        print("✅ Configuration is valid (with warnings)")
    else:
        print("❌ Configuration has errors and cannot be used")

    return len(errors) == 0


def main():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Main validation function"""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Default path
        config_path = os.path.join(
            os.path.dirname(__file__), "router-controller", "config.yml"
        )

    print("🔍 Validating NVIDIA LLM Router Configuration")
    print(f"📁 Config file: {config_path}")
    print()

    is_valid = validate_config_file(config_path)

    if is_valid:
        print("\n🎉 Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
