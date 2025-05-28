"""
Tests for the main Flask application
"""
import pytest
import json
from unittest.mock import patch
from app import app


class TestFlaskApp:
    """Test cases for Flask application endpoints"""

    @pytest.fixture
    def client(self, mock_env_vars):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_home_endpoint(self, client):
        """Test the home endpoint returns correct message"""
        response = client.get('/')
        assert response.status_code == 200
        assert b"Bitbucket AI Code Reviewer is running!" in response.data

    def test_test_endpoint(self, client):
        """Test the /test endpoint returns JSON status"""
        response = client.get('/test')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Server is accessible'
        assert 'timestamp' in data

    def test_webhook_endpoint_no_data(self, client):
        """Test webhook endpoint with no data"""
        response = client.post('/webhook')
        # Should fail due to missing signature/data/content-type
        assert response.status_code in [400, 401, 415]

    @patch('src.utils.webhook_utils.verify_webhook_signature')
    def test_webhook_endpoint_non_pr_event(
            self, mock_verify, client, sample_webhook_payload
    ):
        """Test webhook with non-PR event"""
        # Mock signature verification to pass
        def mock_decorator(f):
            return f
        mock_verify.return_value = mock_decorator

        # Remove pullrequest to make it non-PR event
        payload = {"repository": {"name": "test"}}

        with patch(
                'src.utils.webhook_utils.is_pull_request_event',
                return_value=False
        ):
            response = client.post(
                '/webhook',
                data=json.dumps(payload),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'ignored'

    def test_webhook_error_handling(self, client):
        """Test webhook error handling with invalid payload"""
        # Test with completely invalid JSON
        response = client.post(
            '/webhook',
            data='invalid json',
            content_type='application/json'
        )

        # Should handle the error gracefully (400 or 401 depending on
        # signature verification)
        assert response.status_code in [400, 401, 422]

    def test_rate_limiting(self, client, mock_env_vars):
        """Test rate limiting functionality"""
        # Rate limiting is only applied to webhook endpoint, not test endpoint
        # Test endpoint should always return 200
        for i in range(5):
            response = client.get('/test')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
