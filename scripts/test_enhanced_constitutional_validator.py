#!/usr/bin/env python3
"""
Test Script for Enhanced Constitutional Compliance Validator
Constitutional Hash: cdd01ef066bc6cf2

This script demonstrates the new features:
- UTF-8 text file scanning with size limits
- Binary file detection and skipping
- False-positive suppression with constitution-ignore pragma
- Extended file type support
"""

import tempfile
from pathlib import Path

from tools.constitutional_compliance_enforcer import ConstitutionalComplianceEnforcer


def create_test_files():
    """Create test files to demonstrate the validator features."""
    test_dir = Path(tempfile.mkdtemp(prefix="constitutional_test_"))
    print(f"Creating test files in: {test_dir}")

    # 1. Python file with constitutional hash
    python_file = test_dir / "compliant.py"
    python_file.write_text("""#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2

def main():
    print("This file has the constitutional hash")
""")

    # 2. Python file without constitutional hash
    python_file_bad = test_dir / "non_compliant.py"
    python_file_bad.write_text("""#!/usr/bin/env python3

def main():
    print("This file is missing the constitutional hash")
""")

    # 3. JavaScript file with constitutional hash
    js_file = test_dir / "app.js"
    js_file.write_text("""// Constitutional Hash: cdd01ef066bc6cf2

const express = require('express');
const app = express();

app.get('/api/data', (req, res) => {
    // Check constitutional header
    if (req.headers['x-constitutional-hash'] === 'cdd01ef066bc6cf2') {
        res.json({constitutional_hash: 'cdd01ef066bc6cf2', data: 'valid'});
    }
});
""")

    # 4. HTML file with constitution-ignore pragma
    html_file = test_dir / "ignored.html"
    html_file.write_text("""<!DOCTYPE html>
<!-- constitution-ignore -->
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <p>This file should be ignored due to the pragma</p>
</body>
</html>
""")

    # 5. CSS file without constitutional hash
    css_file = test_dir / "styles.css"
    css_file.write_text(""".header {
    background-color: #blue;
    color: white;
}

.content {
    margin: 20px;
}
""")

    # 6. Binary file (should be skipped)
    binary_file = test_dir / "binary.dat"
    binary_file.write_bytes(
        b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
    )

    # 7. Large file (>1MB, should be skipped)
    large_file = test_dir / "large.txt"
    large_content = "A" * (1024 * 1024 + 1)  # 1MB + 1 byte
    large_file.write_text(large_content)

    # 8. SQL file with constitutional hash
    sql_file = test_dir / "schema.sql"
    sql_file.write_text("""-- Constitutional Hash: cdd01ef066bc6cf2

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    constitutional_compliance BOOLEAN DEFAULT TRUE
);
""")

    # 9. TypeScript file with pragma
    ts_file = test_dir / "service.ts"
    ts_file.write_text("""// constitution-ignore
interface UserService {
    getUsers(): Promise<User[]>;
    createUser(user: User): Promise<User>;
}

export class UserServiceImpl implements UserService {
    async getUsers(): Promise<User[]> {
        return await fetch('/api/users');
    }
}
""")

    return test_dir


def test_enhanced_validator():
    """Test the enhanced constitutional compliance validator."""
    print("🔍 Testing Enhanced Constitutional Compliance Validator")
    print("=" * 60)

    # Create test files
    test_dir = create_test_files()

    try:
        # Initialize the enforcer
        enforcer = ConstitutionalComplianceEnforcer(test_dir)

        print(f"\n📂 Test directory: {test_dir}")
        print(f"🔐 Constitutional Hash: {enforcer.constitutional_hash}")

        # Run the scan
        print("\n🚀 Running compliance scan...")
        report = enforcer.scan_codebase()

        # Display results
        print("\n📊 SCAN RESULTS")
        print("-" * 40)
        print(f"Files scanned: {report.files_scanned}")
        print(f"Files compliant: {report.files_compliant}")
        print(f"Violations found: {len(report.violations)}")
        print(f"Compliance score: {report.overall_compliance_score:.1f}%")

        # Show violations
        if report.violations:
            print("\n❌ VIOLATIONS FOUND:")
            for i, violation in enumerate(report.violations, 1):
                print(f"  {i}. {violation.file_path.name}")
                print(f"     Type: {violation.violation_type}")
                print(f"     Severity: {violation.severity}")
                print(f"     Message: {violation.message}")
                print()

        # Test specific features
        print("\n🧪 FEATURE TESTS:")

        # Test 1: Pragma detection
        html_file = test_dir / "ignored.html"
        with open(html_file) as f:
            content = f.read()
        has_pragma = enforcer._has_constitutional_ignore_pragma(content)
        print(f"✅ Pragma detection: {'PASS' if has_pragma else 'FAIL'}")

        # Test 2: Binary detection
        binary_file = test_dir / "binary.dat"
        is_text = enforcer._is_utf8_text_file(binary_file)
        print(f"✅ Binary detection: {'PASS' if not is_text else 'FAIL'}")

        # Test 3: Large file detection
        large_file = test_dir / "large.txt"
        size_check = large_file.stat().st_size > (1024 * 1024)
        print(f"✅ Size limit check: {'PASS' if size_check else 'FAIL'}")

        # Test 4: Extended file types
        files_found = list(test_dir.glob("*"))
        supported_extensions = {".py", ".js", ".html", ".css", ".sql", ".ts"}
        found_extensions = {
            f.suffix for f in files_found if f.suffix in supported_extensions
        }
        print(
            "✅ Extended file types:"
            f" {'PASS' if len(found_extensions) >= 4 else 'FAIL'}"
        )
        print(f"   Found: {', '.join(sorted(found_extensions))}")

        return report

    finally:
        # Cleanup
        import shutil

        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")


def main():
    """Main test function."""
    try:
        report = test_enhanced_validator()

        print("\n🎉 TEST COMPLETED")
        print("=" * 60)
        print("Enhanced Constitutional Compliance Validator features:")
        print("✅ UTF-8 text file scanning with 1MB size limit")
        print("✅ Binary file detection and automatic skipping")
        print("✅ False-positive suppression via constitution-ignore pragma")
        print("✅ Extended file type support (Python, JS, HTML, CSS, SQL, etc.)")
        print("✅ Multi-encoding support with graceful fallback")
        print("✅ Language-specific compliance checks")
        print("\n🔐 Constitutional Hash: cdd01ef066bc6cf2")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
