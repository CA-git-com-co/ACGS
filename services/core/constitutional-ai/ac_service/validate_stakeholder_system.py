#!/usr/bin/env python3
"""
Validation script for Stakeholder Engagement System

This script validates the stakeholder engagement system implementation
by checking code structure, imports, and basic functionality.
"""

import ast
import pathlib
import sys

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def validate_file_structure():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Validate that all required files exist."""

    required_files = [
        "app/services/stakeholder_engagement.py",
        "app/api/v1/stakeholder_engagement.py",
    ]

    missing_files = [
        file_path
        for file_path in required_files
        if not pathlib.Path(file_path).exists()
    ]

    return not missing_files


def validate_stakeholder_service():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Validate stakeholder engagement service structure."""

    service_file = "app/services/stakeholder_engagement.py"

    try:
        with open(service_file, encoding="utf-8") as f:
            content = f.read()

        # Parse the AST to check for required classes and methods
        tree = ast.parse(content)

        classes_found = []
        methods_found = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_found.append(node.name)

                # Check for methods in classes
                methods_found.extend(
                    f"{node.name}.{item.name}"
                    for item in node.body
                    if isinstance(item, ast.FunctionDef)
                )

        # Required classes
        required_classes = [
            "NotificationChannel",
            "StakeholderRole",
            "NotificationStatus",
            "FeedbackStatus",
            "NotificationRecord",
            "FeedbackRecord",
            "StakeholderEngagementInput",
            "StakeholderEngagementStatus",
            "StakeholderNotificationService",
        ]

        missing_classes = [cls for cls in required_classes if cls not in classes_found]

        if missing_classes:
            return False

        # Required methods in StakeholderNotificationService
        required_methods = [
            "StakeholderNotificationService.initiate_stakeholder_engagement",
            "StakeholderNotificationService.collect_stakeholder_feedback",
            "StakeholderNotificationService.get_engagement_status",
            "StakeholderNotificationService.get_stakeholder_notifications",
            "StakeholderNotificationService.get_stakeholder_feedback",
        ]

        missing_methods = [
            method for method in required_methods if method not in methods_found
        ]

        return not missing_methods

    except Exception:
        return False


def validate_api_endpoints():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Validate API endpoints structure."""

    api_file = "app/api/v1/stakeholder_engagement.py"

    try:
        with open(api_file, encoding="utf-8") as f:
            content = f.read()

        # Check for required endpoint patterns
        required_patterns = [
            '@router.post("/initiate"',
            '@router.get("/status/{amendment_id}"',
            '@router.post("/feedback"',
            '@router.get("/notifications"',
            '@router.get("/feedback/{amendment_id}"',
            '@router.websocket("/ws/{amendment_id}")',
        ]

        missing_patterns = [
            pattern for pattern in required_patterns if pattern not in content
        ]

        return not missing_patterns

    except Exception:
        return False


def validate_constitutional_council_integration():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Validate integration with Constitutional Council StateGraph."""

    graph_file = "app/workflows/constitutional_council_graph.py"

    try:
        with open(graph_file, encoding="utf-8") as f:
            content = f.read()

        # Check for stakeholder engagement imports and usage
        required_imports = [
            "from .services.stakeholder_engagement import",
            "StakeholderNotificationService",
            "StakeholderEngagementInput",
        ]

        missing_imports = [
            import_pattern
            for import_pattern in required_imports
            if import_pattern not in content
        ]

        if missing_imports:
            return False

        # Check for stakeholder service initialization
        return "self.stakeholder_service = StakeholderNotificationService" in content

    except Exception:
        return False


def validate_main_app_integration():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Validate integration with main AC service app."""

    main_file = "app/main.py"

    try:
        with open(main_file, encoding="utf-8") as f:
            content = f.read()

        # Check for stakeholder engagement router import and inclusion
        if "stakeholder_engagement_router" not in content:
            return False

        return not (
            "app.include_router" not in content
            or "stakeholder_engagement_router" not in content
        )

    except Exception:
        return False


def run_validation():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Run all validation checks."""

    checks = [
        ("File Structure", validate_file_structure),
        ("Stakeholder Service", validate_stakeholder_service),
        ("API Endpoints", validate_api_endpoints),
        (
            "Constitutional Council Integration",
            validate_constitutional_council_integration,
        ),
        ("Main App Integration", validate_main_app_integration),
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception:
            results.append((check_name, False))

    # Summary

    passed = 0
    total = len(results)

    for check_name, result in results:
        if result:
            passed += 1

    if passed == total:
        pass

    return passed == total


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
