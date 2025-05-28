"""
pytest configuration and fixtures for AI Code Reviewer tests
"""
import os
import pytest
import tempfile
from unittest.mock import patch


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test-key-12345',
        'BITBUCKET_ACCESS_TOKEN': 'test-bitbucket-token',
        'WEBHOOK_SECRET': 'test-webhook-secret',
        'PORT': '5000',
        'API_RATE_LIMIT': '60'
    }):
        yield


@pytest.fixture
def sample_pr_info():
    """Sample PR info for testing"""
    return {
        'id': 123,
        'title': 'Test PR',
        'repository': {
            'full_name': 'test-user/test-repo'
        },
        'links': {
            'diff': {
                'href': 'https://api.bitbucket.org/2.0/repositories/test-user/test-repo/pullrequests/123/diff'
            }
        }
    }


@pytest.fixture
def sample_diff():
    """Sample diff content for testing"""
    return """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 def hello():
-    print("Hello")
+    print("Hello World")
+    # Added a comment
+    return "Hello World"
"""


@pytest.fixture
def sample_webhook_payload():
    """Sample Bitbucket webhook payload"""
    return {
        "pullrequest": {
            "id": 123,
            "title": "Test Pull Request",
            "source": {
                "branch": {
                    "name": "feature-branch"
                }
            },
            "destination": {
                "branch": {
                    "name": "main"
                },
                "repository": {
                    "full_name": "test-user/test-repo"
                }
            },
            "links": {
                "diff": {
                    "href": "https://api.bitbucket.org/2.0/repositories/test-user/test-repo/pullrequests/123/diff"
                }
            }
        }
    }


@pytest.fixture
def temp_log_dir():
    """Create temporary log directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = os.path.join(tmpdir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        with patch('app.LOG_DIR', log_dir):
            yield log_dir
