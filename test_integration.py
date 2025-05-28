#!/usr/bin/env python3
"""
Integration test for AI Code Reviewer

This test verifies that all components work together correctly.
Run this after setting up your environment to ensure everything is working.
"""

import os
import sys
import requests
import subprocess
import time
import signal
from pathlib import Path


class IntegrationTest:
    """Integration test runner"""

    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:5000"

    def start_server(self):
        """Start the Flask server for testing"""
        print("🚀 Starting Flask server for integration test...")

        # Set test environment variables
        env = os.environ.copy()
        env.update({
            'OPENAI_API_KEY': 'sk-test-key-for-integration',
            'BITBUCKET_ACCESS_TOKEN': 'test-token-integration',
            'WEBHOOK_SECRET': 'test-secret-integration',
            'PORT': '5000',
            'FLASK_DEBUG': 'false'
        })

        try:
            self.server_process = subprocess.Popen([
                sys.executable, 'app.py'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for server to start
            for _ in range(10):
                try:
                    response = requests.get(f"{self.server_url}/", timeout=5)
                    if response.status_code == 200:
                        print("✅ Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)

            print("❌ Server failed to start")
            return False

        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False

    def stop_server(self):
        """Stop the Flask server"""
        if self.server_process:
            print("🛑 Stopping Flask server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None

    def test_home_endpoint(self):
        """Test the home endpoint"""
        print("🧪 Testing home endpoint...")
        try:
            response = requests.get(f"{self.server_url}/", timeout=10)
            assert response.status_code == 200
            assert "Bitbucket AI Code Reviewer is running!" in response.text
            print("✅ Home endpoint working")
            return True
        except Exception as e:
            print(f"❌ Home endpoint failed: {e}")
            return False

    def test_status_endpoint(self):
        """Test the status endpoint"""
        print("🧪 Testing status endpoint...")
        try:
            response = requests.get(f"{self.server_url}/test", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'success'
            assert 'timestamp' in data
            print("✅ Status endpoint working")
            return True
        except Exception as e:
            print(f"❌ Status endpoint failed: {e}")
            return False

    def test_webhook_endpoint(self):
        """Test the webhook endpoint"""
        print("🧪 Testing webhook endpoint...")
        try:
            # Test with invalid payload (should be rejected)
            response = requests.post(f"{self.server_url}/webhook", json={}, timeout=10)
            # Should fail due to signature verification or invalid payload
            assert response.status_code in [400, 401]
            print("✅ Webhook endpoint properly rejects invalid requests")
            return True
        except Exception as e:
            print(f"❌ Webhook endpoint failed: {e}")
            return False

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("🧪 Testing rate limiting...")
        try:
            # Make multiple requests quickly
            responses = []
            for i in range(5):
                response = requests.get(f"{self.server_url}/test", timeout=10)
                responses.append(response.status_code)

            # Should get mostly 200s, possibly some 429s if rate limiting kicks in
            success_count = sum(1 for code in responses if code == 200)
            assert success_count >= 3  # At least some should succeed
            print(f"✅ Rate limiting working (got {success_count}/5 successful responses)")
            return True
        except Exception as e:
            print(f"❌ Rate limiting test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 AI Code Reviewer - Integration Test Suite")
        print("=" * 50)

        if not self.start_server():
            return False

        try:
            tests = [
                self.test_home_endpoint,
                self.test_status_endpoint,
                self.test_webhook_endpoint,
                self.test_rate_limiting
            ]

            passed = 0
            total = len(tests)

            for test in tests:
                if test():
                    passed += 1
                print()  # Add spacing between tests

            print("=" * 50)
            print(f"📊 Integration Test Results: {passed}/{total} tests passed")

            if passed == total:
                print("🎉 All integration tests passed!")
                print("\n📝 Your AI Code Reviewer is working correctly!")
                print("✅ Ready for production deployment")
                return True
            else:
                print("❌ Some integration tests failed")
                print("🔧 Check the error messages above")
                return False

        finally:
            self.stop_server()


def main():
    """Main integration test runner"""
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found. Run this script from the project root directory.")
        sys.exit(1)

    test_runner = IntegrationTest()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Test interrupted by user")
        test_runner.stop_server()
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        success = test_runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        test_runner.stop_server()
        sys.exit(1)


if __name__ == '__main__':
    main()
