"""
Tests for webhook utilities
"""
import hmac
import hashlib
from unittest.mock import patch
from flask import Flask
from src.utils.webhook_utils import (
    verify_webhook_signature,
    is_pull_request_event,
    extract_pr_info
)


class TestWebhookUtils:
    """Test cases for webhook utility functions"""

    def test_is_pull_request_event_with_header(self):
        """Test PR event detection with X-Event-Key header"""
        payload = {}
        headers = {'X-Event-Key': 'pullrequest:created'}

        assert is_pull_request_event(payload, headers) is True

        headers = {'X-Event-Key': 'pullrequest:updated'}
        assert is_pull_request_event(payload, headers) is True

        headers = {'X-Event-Key': 'repository:push'}
        assert is_pull_request_event(payload, headers) is False

    def test_is_pull_request_event_with_payload(self):
        """Test PR event detection with payload content"""
        payload = {'pullrequest': {'id': 123}}
        headers = {}

        assert is_pull_request_event(payload, headers) is True

        payload = {'repository': {'name': 'test'}}
        assert is_pull_request_event(payload, headers) is False

    def test_is_pull_request_event_exception(self):
        """Test PR event detection with exception"""
        # Invalid payload that might cause exception
        payload = None
        headers = {}

        result = is_pull_request_event(payload, headers)
        assert result is False

    def test_extract_pr_info(self, sample_webhook_payload):
        """Test PR info extraction"""
        result = extract_pr_info(sample_webhook_payload)

        assert result['id'] == 123
        assert result['title'] == 'Test Pull Request'
        assert result['source_branch'] == 'feature-branch'
        assert result['destination_branch'] == 'main'
        assert result['repository']['full_name'] == 'test-user/test-repo'
        assert 'links' in result

    def test_extract_pr_info_empty_payload(self):
        """Test PR info extraction with empty payload"""
        result = extract_pr_info({})

        assert result['id'] is None
        assert result['title'] is None
        assert result['source_branch'] is None
        assert result['destination_branch'] is None
        assert result['repository']['full_name'] is None

    def test_verify_webhook_signature_no_secret(self):
        """Test webhook signature verification without secret"""
        app = Flask(__name__)

        @verify_webhook_signature
        def test_function():
            return "success"

        with app.test_request_context('/', method='POST', data=b'test'):
            with patch.dict('os.environ', {}, clear=True):
                result = test_function()
                assert result == "success"

    def test_verify_webhook_signature_no_header(self):
        """Test webhook signature verification without signature header"""
        app = Flask(__name__)

        @verify_webhook_signature
        def test_function():
            return "success"

        with app.test_request_context('/', method='POST', data=b'test'):
            with patch(
                'src.utils.webhook_utils.WEBHOOK_SECRET', 'test-secret'
            ):
                result = test_function()
                # Should return error JSON response tuple
                assert isinstance(result, tuple)
                assert result[1] == 401

    def test_verify_webhook_signature_valid(self):
        """Test webhook signature verification with valid signature"""
        app = Flask(__name__)

        @verify_webhook_signature
        def test_function():
            return "success"

        # Create valid signature
        secret = 'test-secret'
        payload = b'test payload'
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        headers = {'X-Hub-Signature-256': f'sha256={signature}'}

        with app.test_request_context(
                '/', method='POST', data=payload, headers=headers
        ):
            with patch('src.utils.webhook_utils.WEBHOOK_SECRET', secret):
                result = test_function()
                assert result == "success"

    def test_verify_webhook_signature_invalid(self):
        """Test webhook signature verification with invalid signature"""
        app = Flask(__name__)

        @verify_webhook_signature
        def test_function():
            return "success"

        headers = {'X-Hub-Signature-256': 'sha256=invalid-signature'}

        with app.test_request_context(
                '/', method='POST', data=b'test', headers=headers
        ):
            with patch(
                'src.utils.webhook_utils.WEBHOOK_SECRET', 'test-secret'
            ):
                result = test_function()
                # Should return error JSON response tuple
                assert isinstance(result, tuple)
                assert result[1] == 401

    def test_verify_webhook_signature_different_formats(self):
        """Test webhook signature verification with different header formats"""
        app = Flask(__name__)

        @verify_webhook_signature
        def test_function():
            return "success"

        secret = 'test-secret'
        payload = b'test payload'
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Test without sha256= prefix
        headers = {'X-Hub-Signature': signature}

        with app.test_request_context(
                '/', method='POST', data=payload, headers=headers
        ):
            with patch('src.utils.webhook_utils.WEBHOOK_SECRET', secret):
                result = test_function()
                assert result == "success"
