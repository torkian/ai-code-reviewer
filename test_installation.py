#!/usr/bin/env python3
"""
Basic installation test for Bitbucket AI Code Reviewer

This script verifies that:
1. All required dependencies are installed
2. Environment variables are configured
3. The application can start successfully
4. API connections work properly

Run this after setting up your .env file to verify the installation.
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_dependencies():
    """Check if all required Python packages are installed"""
    print("🔍 Checking dependencies...")

    required_packages = [
        'flask', 'requests', 'dotenv', 'werkzeug', 'gunicorn'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if importlib.util.find_spec(package) is None:
                missing_packages.append(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False

    print("✅ All dependencies are installed")
    return True

def check_environment():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment configuration...")

    # Load .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file found and loaded")
    else:
        print("⚠️  .env file not found - using system environment variables")

    required_vars = ['OPENAI_API_KEY']
    auth_vars = ['BITBUCKET_ACCESS_TOKEN', 'BITBUCKET_APP_PASSWORD']
    optional_vars = ['WEBHOOK_SECRET', 'PORT', 'API_RATE_LIMIT']

    # Check if we're in a CI environment
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

    # Check required variables
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    # Check auth variables (at least one should be set)
    auth_configured = any(os.getenv(var) for var in auth_vars)

    if missing_required:
        if is_ci:
            print(f"⚠️  Missing required variables: {', '.join(missing_required)} (expected in CI)")
        else:
            print(f"❌ Missing required variables: {', '.join(missing_required)}")
            return False

    if not auth_configured:
        if is_ci:
            print(f"⚠️  Missing authentication: Set either {' or '.join(auth_vars)} (expected in CI)")
        else:
            print(f"❌ Missing authentication: Set either {' or '.join(auth_vars)}")
            return False

    if missing_required or not auth_configured:
        if is_ci:
            print("✅ Configuration check passed (CI environment)")
        else:
            return False
    else:
        print("✅ Required environment variables are configured")

    # Check optional variables
    configured_optional = [var for var in optional_vars if os.getenv(var)]
    if configured_optional:
        print(f"✅ Optional variables configured: {', '.join(configured_optional)}")

    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI API connection...")

    # Check if we're in a CI environment
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

    try:
        import requests
        api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            if is_ci:
                print("⚠️  OpenAI API key not found (expected in CI environment)")
                return True  # Don't fail CI for missing API key
            else:
                print("❌ OpenAI API key not found")
                return False

        # Test API key format
        if not api_key.startswith('sk-'):
            if is_ci:
                print("⚠️  OpenAI API key format appears invalid (expected in CI environment)")
                return True  # Don't fail CI for placeholder key
            else:
                print("❌ OpenAI API key format appears invalid")
                return False

        # Simple API test (just check authentication)
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )

        if response.status_code == 200:
            print("✅ OpenAI API connection successful")
            return True
        elif response.status_code == 401:
            print("❌ OpenAI API authentication failed - check your API key")
            return False
        else:
            print(f"⚠️  OpenAI API returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to OpenAI API - check internet connection")
        return False
    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        return False

def test_application_startup():
    """Test if the application can start"""
    print("\n🔍 Testing application startup...")

    try:
        # Import the main app
        from app import app

        # Test app creation
        if app is None:
            print("❌ Failed to create Flask application")
            return False

        # Test app configuration
        test_client = app.test_client()
        response = test_client.get('/')

        if response.status_code == 200:
            print("✅ Application starts successfully")
            print(f"   Response: {response.get_data(as_text=True)}")
            return True
        else:
            print(f"❌ Application startup failed with status {response.status_code}")
            return False

    except ImportError as e:
        print(f"❌ Failed to import application: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Application startup test failed: {str(e)}")
        return False

def main():
    """Run all installation tests"""
    print("🧪 Bitbucket AI Code Reviewer - Installation Test")
    print("=" * 50)

    tests = [
        check_dependencies,
        check_environment,
        test_openai_connection,
        test_application_startup
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Installation test successful! Your setup is ready.")
        print("\n📝 Next steps:")
        print("   1. Set up a Bitbucket webhook pointing to your server")
        print("   2. Create a test pull request to verify the integration")
        print("   3. Check the logs for any issues")
        return True
    else:
        print("❌ Installation test failed. Please fix the issues above.")
        print("\n📝 Common solutions:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Copy .env.example to .env and configure your API keys")
        print("   - Verify your OpenAI API key is valid and has credits")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
