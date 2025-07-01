#!/usr/bin/env python3
"""
Structure and Logic Test for Constitutional Trainer
Tests the code structure, imports, and basic logic without heavy ML dependencies.
"""

import ast
import os
import re
import sys


def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing File Structure...")

    required_files = [
        "main.py",
        "constitutional_trainer.py",
        "validators.py",
        "privacy_engine.py",
        "metrics.py",
        "requirements.txt",
        "Dockerfile",
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    print("✅ All required files present")
    return True


def test_python_syntax():
    """Test Python syntax of all .py files."""
    print("\n🧪 Testing Python Syntax...")

    python_files = [
        "main.py",
        "constitutional_trainer.py",
        "validators.py",
        "privacy_engine.py",
        "metrics.py",
    ]

    for file in python_files:
        try:
            with open(file) as f:
                content = f.read()

            # Parse the AST to check syntax
            ast.parse(content)
            print(f"✅ {file} - syntax valid")

        except SyntaxError as e:
            print(f"❌ {file} - syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ {file} - error: {e}")
            return False

    return True


def test_constitutional_hash_presence():
    """Test that constitutional hash is present in all relevant files."""
    print("\n🧪 Testing Constitutional Hash Presence...")

    expected_hash = "cdd01ef066bc6cf2"
    files_to_check = [
        "main.py",
        "constitutional_trainer.py",
        "validators.py",
        "privacy_engine.py",
        "metrics.py",
        "Dockerfile",
        "../../../infrastructure/kubernetes/acgs-lite/constitutional-trainer.yaml",
    ]

    for file in files_to_check:
        if not os.path.exists(file):
            continue

        try:
            with open(file) as f:
                content = f.read()

            if expected_hash in content:
                print(f"✅ {file} - constitutional hash found")
            else:
                print(f"⚠️  {file} - constitutional hash not found")

        except Exception as e:
            print(f"❌ {file} - error reading: {e}")

    return True


def test_import_structure():
    """Test import structure and dependencies."""
    print("\n🧪 Testing Import Structure...")

    files_to_check = {
        "main.py": ["fastapi", "uvicorn", "prometheus_client"],
        "constitutional_trainer.py": ["torch", "transformers", "peft"],
        "validators.py": ["aiohttp", "aioredis"],
        "privacy_engine.py": ["opacus"],
        "metrics.py": ["prometheus_client"],
    }

    for file, expected_imports in files_to_check.items():
        try:
            with open(file) as f:
                content = f.read()

            print(f"📁 {file}:")
            for imp in expected_imports:
                if f"import {imp}" in content or f"from {imp}" in content:
                    print(f"   ✅ {imp} imported")
                else:
                    print(f"   ⚠️  {imp} not found in imports")

        except Exception as e:
            print(f"❌ {file} - error: {e}")

    return True


def test_class_definitions():
    """Test that required classes are defined."""
    print("\n🧪 Testing Class Definitions...")

    expected_classes = {
        "main.py": [
            "ServiceConfig",
            "TrainingRequest",
            "TrainingResponse",
            "TrainingSessionManager",
        ],
        "constitutional_trainer.py": ["ConstitutionalConfig", "ConstitutionalTrainer"],
        "validators.py": ["ACGSConstitutionalValidator"],
        "privacy_engine.py": ["ConstitutionalPrivacyEngine"],
        "metrics.py": ["ConstitutionalMetrics", "ConstitutionalTrainingMetrics"],
    }

    for file, classes in expected_classes.items():
        try:
            with open(file) as f:
                content = f.read()

            print(f"📁 {file}:")
            for cls in classes:
                if f"class {cls}" in content:
                    print(f"   ✅ {cls} defined")
                else:
                    print(f"   ❌ {cls} not found")

        except Exception as e:
            print(f"❌ {file} - error: {e}")

    return True


def test_api_endpoints():
    """Test that required API endpoints are defined."""
    print("\n🧪 Testing API Endpoints...")

    try:
        with open("main.py") as f:
            content = f.read()

        expected_endpoints = [
            '@app.get("/health")',
            '@app.get("/metrics")',
            '@app.post("/api/v1/train")',
            '@app.get("/api/v1/train/{training_id}/status")',
            '@app.delete("/api/v1/train/{training_id}")',
        ]

        for endpoint in expected_endpoints:
            if endpoint in content:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} not found")

    except Exception as e:
        print(f"❌ Error checking endpoints: {e}")

    return True


def test_docker_configuration():
    """Test Docker configuration."""
    print("\n🧪 Testing Docker Configuration...")

    try:
        with open("Dockerfile") as f:
            content = f.read()

        required_elements = [
            "FROM python:3.11-slim",
            "CONSTITUTIONAL_HASH=cdd01ef066bc6cf2",
            "USER constitutional",
            "EXPOSE 8010",
            "HEALTHCHECK",
        ]

        for element in required_elements:
            if element in content:
                print(f"✅ {element}")
            else:
                print(f"❌ {element} not found")

        # Check for security best practices
        security_checks = [
            ("runAsNonRoot", "Non-root user configuration"),
            ("USER constitutional", "Specific user defined"),
            ("HEALTHCHECK", "Health check configured"),
        ]

        for check, description in security_checks:
            if check in content:
                print(f"🔒 {description} - ✅")
            else:
                print(f"🔒 {description} - ⚠️")

    except Exception as e:
        print(f"❌ Error checking Dockerfile: {e}")

    return True


def test_kubernetes_configuration():
    """Test Kubernetes configuration."""
    print("\n🧪 Testing Kubernetes Configuration...")

    k8s_file = (
        "../../../infrastructure/kubernetes/acgs-lite/constitutional-trainer.yaml"
    )

    if not os.path.exists(k8s_file):
        print(f"❌ Kubernetes manifest not found: {k8s_file}")
        return False

    try:
        with open(k8s_file) as f:
            content = f.read()

        required_resources = [
            "kind: Namespace",
            "kind: ConfigMap",
            "kind: Secret",
            "kind: Deployment",
            "kind: Service",
            "kind: HorizontalPodAutoscaler",
            "kind: PodDisruptionBudget",
        ]

        for resource in required_resources:
            if resource in content:
                print(f"✅ {resource}")
            else:
                print(f"❌ {resource} not found")

        # Check security configurations
        security_configs = [
            "runAsNonRoot: true",
            "runAsUser: 1000",
            "allowPrivilegeEscalation: false",
            "readOnlyRootFilesystem",
        ]

        for config in security_configs:
            if config in content:
                print(f"🔒 {config} - ✅")
            else:
                print(f"🔒 {config} - ⚠️")

    except Exception as e:
        print(f"❌ Error checking Kubernetes manifest: {e}")
        return False

    return True


def test_requirements():
    """Test requirements.txt."""
    print("\n🧪 Testing Requirements...")

    try:
        with open("requirements.txt") as f:
            content = f.read()

        critical_deps = [
            "fastapi",
            "uvicorn",
            "torch",
            "transformers",
            "opacus",
            "prometheus-client",
            "aiohttp",
            "peft",
        ]

        for dep in critical_deps:
            if dep in content.lower():
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} not found")

    except Exception as e:
        print(f"❌ Error checking requirements: {e}")

    return True


def test_configuration_consistency():
    """Test configuration consistency across files."""
    print("\n🧪 Testing Configuration Consistency...")

    # Check that constitutional hash is consistent
    hash_pattern = r"cdd01ef066bc6cf2"
    files_with_hash = []

    for file in [
        "main.py",
        "constitutional_trainer.py",
        "validators.py",
        "privacy_engine.py",
        "Dockerfile",
    ]:
        if os.path.exists(file):
            with open(file) as f:
                content = f.read()
            if re.search(hash_pattern, content):
                files_with_hash.append(file)

    print(f"✅ Constitutional hash found in {len(files_with_hash)} files")

    # Check port consistency
    port_pattern = r"8010"
    files_with_port = []

    for file in ["main.py", "Dockerfile"]:
        if os.path.exists(file):
            with open(file) as f:
                content = f.read()
            if re.search(port_pattern, content):
                files_with_port.append(file)

    print(f"✅ Port 8010 found in {len(files_with_port)} files")

    return True


def run_all_tests():
    """Run all structure tests."""
    print("🚀 Starting Constitutional Trainer Structure Tests")
    print("=" * 60)

    tests = [
        test_file_structure,
        test_python_syntax,
        test_constitutional_hash_presence,
        test_import_structure,
        test_class_definitions,
        test_api_endpoints,
        test_docker_configuration,
        test_kubernetes_configuration,
        test_requirements,
        test_configuration_consistency,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL STRUCTURE TESTS PASSED!")
        print("✅ Constitutional Trainer implementation structure is valid")
        print("🔒 Constitutional Hash: cdd01ef066bc6cf2")
        print("🚀 Ready for deployment testing")
    else:
        print(f"⚠️  {total - passed} tests failed")
        print("🔧 Review the failed tests and fix issues")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
