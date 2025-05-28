#!/usr/bin/env python3
"""
Test runner for AI Code Reviewer

This script runs the full test suite and can be used with Anaconda environments.
"""

import sys
import os
import subprocess
import importlib.util


def check_environment():
    """Check if we're in the right environment with required packages"""
    print("🔍 Checking test environment...")

    required_packages = ['pytest', 'flask', 'requests']
    missing_packages = []

    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -r requirements.txt")
        return False

    print("✅ All required packages are available")
    return True


def run_tests():
    """Run the test suite"""
    print("\n🧪 Running AI Code Reviewer Test Suite")
    print("=" * 50)

    # Set PYTHONPATH to include current directory
    env = os.environ.copy()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env['PYTHONPATH'] = current_dir

    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/',
            '-v',
            '--tb=short',
            '--color=yes'
        ],
        cwd=current_dir,
        env=env,
        capture_output=False,
        text=True
        )

        print("\n" + "=" * 50)
        if result.returncode == 0:
            print("🎉 All tests passed!")
            print("\n📝 Next steps:")
            print("   1. Your code is working correctly")
            print("   2. Ready for deployment")
            print("   3. Consider adding more tests for new features")
        else:
            print("❌ Some tests failed")
            print("\n🔧 Troubleshooting:")
            print("   1. Check the error messages above")
            print("   2. Ensure all environment variables are set")
            print("   3. Verify API credentials are correct")

        return result.returncode == 0

    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_specific_test(test_name):
    """Run a specific test file or test function"""
    print(f"\n🎯 Running specific test: {test_name}")

    # Set PYTHONPATH
    env = os.environ.copy()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env['PYTHONPATH'] = current_dir

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            test_name,
            '-v',
            '--tb=long',
            '--color=yes'
        ],
        cwd=current_dir,
        env=env,
        capture_output=False,
        text=True
        )

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def main():
    """Main test runner"""
    print("🧪 AI Code Reviewer - Test Runner")
    print("Compatible with Anaconda environments")
    print()

    # Check if we should run specific test
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if not check_environment():
            sys.exit(1)
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)

    # Run full test suite
    if not check_environment():
        sys.exit(1)

    success = run_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
