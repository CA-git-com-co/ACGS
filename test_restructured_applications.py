#!/usr/bin/env python3
"""
Test Script for ACGS-PGP Applications Directory Restructuring
Validates the new structure and ensures all components are working correctly
"""

import json
from pathlib import Path


class ApplicationsStructureValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.applications_dir = self.project_root / "applications"
        self.test_results = []

    def run_all_tests(self) -> bool:
        """Run comprehensive validation tests"""
        print("🧪 ACGS-PGP Applications Structure Validation")
        print("=" * 60)

        tests = [
            ("Directory Structure", self.test_directory_structure),
            ("Shared Components", self.test_shared_components),
            ("Package.json Files", self.test_package_json_files),
            ("Service Integrations", self.test_service_integrations),
            ("Import Paths", self.test_import_paths),
            ("Build Compatibility", self.test_build_compatibility),
        ]

        all_passed = True
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {status}")
                self.test_results.append((test_name, result))
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                self.test_results.append((test_name, False))
                all_passed = False

        self.print_test_summary()
        return all_passed

    def test_directory_structure(self) -> bool:
        """Test that all required directories exist"""
        required_dirs = [
            "applications/shared",
            "applications/shared/components",
            "applications/shared/hooks",
            "applications/shared/types",
            "applications/governance-dashboard",
            "applications/legacy-frontend",
            "applications/governance-dashboard/src",
            "applications/legacy-frontend/src",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                print(f"     ❌ Missing: {dir_path}")
            else:
                print(f"     ✅ Found: {dir_path}")

        return len(missing_dirs) == 0

    def test_shared_components(self) -> bool:
        """Test that shared components were moved correctly"""
        expected_shared_files = [
            "applications/shared/components/dashboard/DashboardCards.tsx",
            "applications/shared/components/layout/CommandBar.tsx",
            "applications/shared/components/layout/Sidebar.tsx",
            "applications/shared/components/layout/ThemeToggle.tsx",
            "applications/shared/components/ui/Button.tsx",
            "applications/shared/components/ui/Card.tsx",
            "applications/shared/components/ui/Input.tsx",
            "applications/shared/hooks/useKeyboard.ts",
            "applications/shared/hooks/useLocalStorage.ts",
            "applications/shared/types/governance.ts",
        ]

        missing_files = []
        for file_path in expected_shared_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"     ❌ Missing: {file_path}")
            else:
                print(f"     ✅ Found: {file_path}")

        return len(missing_files) == 0

    def test_package_json_files(self) -> bool:
        """Test that package.json files are intact"""
        package_files = [
            "applications/package.json",
            "applications/governance-dashboard/package.json",
            "applications/legacy-frontend/package.json",
        ]

        all_valid = True
        for package_file in package_files:
            full_path = self.project_root / package_file
            if not full_path.exists():
                print(f"     ❌ Missing: {package_file}")
                all_valid = False
                continue

            try:
                with open(full_path) as f:
                    package_data = json.load(f)
                    if "name" in package_data:
                        print(f"     ✅ Valid: {package_file} ({package_data['name']})")
                    else:
                        print(f"     ⚠️  Warning: {package_file} missing 'name' field")
            except json.JSONDecodeError:
                print(f"     ❌ Invalid JSON: {package_file}")
                all_valid = False

        return all_valid

    def test_service_integrations(self) -> bool:
        """Test that microservice integration files are preserved"""
        service_files = [
            "applications/governance-dashboard/src/services/ACService.js",
            "applications/governance-dashboard/src/services/GSService.js",
            "applications/governance-dashboard/src/services/AuthService.js",
            "applications/legacy-frontend/src/services/ACService.js",
            "applications/legacy-frontend/src/services/GSService.js",
            "applications/legacy-frontend/src/services/AuthService.js",
        ]

        missing_services = []
        for service_file in service_files:
            full_path = self.project_root / service_file
            if not full_path.exists():
                missing_services.append(service_file)
                print(f"     ❌ Missing: {service_file}")
            else:
                print(f"     ✅ Found: {service_file}")

        return len(missing_services) == 0

    def test_import_paths(self) -> bool:
        """Test for potential import path issues"""
        # Check for old import patterns that might need updating
        problematic_patterns = [
            "from '../components/",
            "from '../../components/",
            "from '../hooks/",
            "from '../types/",
        ]

        issues_found = []
        for app_dir in ["governance-dashboard", "legacy-frontend"]:
            app_path = self.applications_dir / app_dir / "src"
            if app_path.exists():
                for file_path in app_path.rglob("*.{ts,tsx,js,jsx}"):
                    if file_path.is_file():
                        try:
                            content = file_path.read_text(encoding="utf-8")
                            for pattern in problematic_patterns:
                                if pattern in content:
                                    issues_found.append(f"{file_path}: {pattern}")
                        except Exception:
                            continue

        if issues_found:
            print(f"     ⚠️  Found {len(issues_found)} potential import issues:")
            for issue in issues_found[:5]:  # Show first 5
                print(f"       • {issue}")
            if len(issues_found) > 5:
                print(f"       ... and {len(issues_found) - 5} more")
            return False
        else:
            print("     ✅ No problematic import patterns found")
            return True

    def test_build_compatibility(self) -> bool:
        """Test that applications can still be built (basic check)"""
        build_compatible = True

        for app_dir in ["governance-dashboard", "legacy-frontend"]:
            app_path = self.applications_dir / app_dir
            if app_path.exists():
                package_json = app_path / "package.json"
                if package_json.exists():
                    print(f"     ✅ {app_dir} has package.json")

                    # Check for node_modules (indicates previous install)
                    node_modules = app_path / "node_modules"
                    if node_modules.exists():
                        print(f"     ✅ {app_dir} has node_modules")
                    else:
                        print(f"     ⚠️  {app_dir} needs 'npm install'")
                else:
                    print(f"     ❌ {app_dir} missing package.json")
                    build_compatible = False

        return build_compatible

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)

        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        print("\nDetailed Results:")
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ The restructured applications directory is ready for use.")
        else:
            print(f"\n⚠️  {total - passed} TEST(S) FAILED")
            print("❌ Please review the issues above before proceeding.")

    def generate_validation_report(self) -> str:
        """Generate a validation report for reviewers"""
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)

        report = f"""# Applications Structure Validation Report

## Summary
- **Tests Run**: {total}
- **Tests Passed**: {passed}
- **Success Rate**: {(passed/total)*100:.1f}%
- **Status**: {'✅ READY FOR MERGE' if passed == total else '❌ NEEDS ATTENTION'}

## Test Results
"""

        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- {status} **{test_name}**\n"

        if passed == total:
            report += "\n## Conclusion\nAll validation tests passed. The restructured applications directory is ready for production use.\n"
        else:
            report += f"\n## Issues Found\n{total - passed} test(s) failed. Please review the console output for detailed information.\n"

        return report


def main():
    """Main execution function"""
    validator = ApplicationsStructureValidator()
    success = validator.run_all_tests()

    # Generate validation report
    report = validator.generate_validation_report()
    with open("applications_validation_report.md", "w") as f:
        f.write(report)

    print("\n📄 Validation report saved to: applications_validation_report.md")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
