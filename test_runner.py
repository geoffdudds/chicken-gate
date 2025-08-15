#!/usr/bin/env python3
"""
Test runner script for the chicken gate project.
Handles testing with and without pytest, and provides environment setup.
"""

import sys
import subprocess
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def check_pytest_available():
    """Check if pytest is available"""
    try:
        import importlib.util
        return importlib.util.find_spec('pytest') is not None
    except ImportError:
        return False


def run_with_pytest():
    """Run tests using pytest"""
    print("🧪 Running tests with pytest...")

    # Basic pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "test/",
        "-v",
        "--tb=short"
    ]

    # Add coverage if available
    try:
        import importlib.util
        if importlib.util.find_spec('pytest_cov') is not None:
            cmd.extend(["--cov=src/chicken_gate", "--cov-report=term-missing"])
            print("📊 Coverage reporting enabled")
    except ImportError:
        print("ℹ️  Install pytest-cov for coverage reporting")

    return subprocess.run(cmd, cwd=project_root).returncode


def run_manual_tests():
    """Run tests manually without pytest"""
    print("🔧 Running tests manually (pytest not available)...")

    test_files = [
        "test/test_gate_comprehensive.py",
        "test/test_gate_integration.py",
        "test/test_gate.py",
        "test/test_timer.py"
    ]

    passed = 0
    failed = 0

    for test_file in test_files:
        test_path = project_root / test_file
        if test_path.exists():
            print(f"\n📄 Running {test_file}...")
            result = subprocess.run([sys.executable, str(test_path)], cwd=project_root)
            if result.returncode == 0:
                passed += 1
                print(f"✅ {test_file} PASSED")
            else:
                failed += 1
                print(f"❌ {test_file} FAILED")
        else:
            print(f"⚠️  {test_file} not found")

    print(f"\n📊 Test Summary: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def run_fast_tests():
    """Run tests with faster timing to avoid long waits"""
    if check_pytest_available():
        print("🚀 Running fast tests with pytest...")
        cmd = [
            sys.executable, "-m", "pytest",
            "test/",
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
            "-m", "not slow"  # Skip tests marked as slow
        ]
        return subprocess.run(cmd, cwd=project_root).returncode
    else:
        return run_manual_tests()


def run_unit_tests_only():
    """Run only unit tests (no hardware dependencies)"""
    if check_pytest_available():
        cmd = [
            sys.executable, "-m", "pytest",
            "test/test_gate_comprehensive.py",
            "-v", "-m", "not hardware"
        ]
        return subprocess.run(cmd, cwd=project_root).returncode
    else:
        print("🔧 Running unit tests manually...")
        test_path = project_root / "test/test_gate_comprehensive.py"
        if test_path.exists():
            return subprocess.run([sys.executable, str(test_path)], cwd=project_root).returncode
        else:
            print("❌ Unit test file not found")
            return 1


def run_integration_tests_only():
    """Run only integration tests (with mock hardware)"""
    if check_pytest_available():
        cmd = [
            sys.executable, "-m", "pytest",
            "test/test_gate_integration.py",
            "-v", "-m", "not hardware"
        ]
        return subprocess.run(cmd, cwd=project_root).returncode
    else:
        print("🔧 Running integration tests manually...")
        test_path = project_root / "test/test_gate_integration.py"
        if test_path.exists():
            return subprocess.run([sys.executable, str(test_path)], cwd=project_root).returncode
        else:
            print("❌ Integration test file not found")
            return 1


def main():
    """Main test runner"""
    print("🐔 Chicken Gate Test Runner")
    print("=" * 50)

    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()

        if test_type == "unit":
            return run_unit_tests_only()
        elif test_type == "integration":
            return run_integration_tests_only()
        elif test_type == "manual":
            return run_manual_tests()
        elif test_type == "fast":
            return run_fast_tests()
        elif test_type == "help":
            print("Usage: python test_runner.py [unit|integration|manual|fast|help]")
            print("  unit        - Run only unit tests")
            print("  integration - Run only integration tests")
            print("  manual      - Run tests without pytest")
            print("  fast        - Run tests quickly (skip slow tests)")
            print("  help        - Show this help")
            print("  (no args)   - Run all tests with best available method")
            return 0
        else:
            print(f"❌ Unknown test type: {test_type}")
            return 1    # Default: run all tests with best available method
    if check_pytest_available():
        return run_with_pytest()
    else:
        print("ℹ️  pytest not available, running manual tests")
        return run_manual_tests()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
