"""
Tests for the main Flask application
"""
import pytest
import json
from unittest.mock import patch, MagicMock
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
        # Should fail due to missing signature/data
        assert response.status_code in [400, 401]
    
    @patch('src.utils.webhook_utils.verify_webhook_signature')
    def test_webhook_endpoint_non_pr_event(self, mock_verify, client, sample_webhook_payload):
        """Test webhook with non-PR event"""
        # Mock signature verification to pass
        def mock_decorator(f):
            return f
        mock_verify.return_value = mock_decorator
        
        # Remove pullrequest to make it non-PR event
        payload = {"repository": {"name": "test"}}
        
        with patch('src.utils.webhook_utils.is_pull_request_event', return_value=False):
            response = client.post('/webhook', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'ignored'
    
    @patch('src.utils.webhook_utils.verify_webhook_signature')
    @patch('src.utils.webhook_utils.is_pull_request_event')
    @patch('src.utils.webhook_utils.extract_pr_info')
    @patch('src.utils.bitbucket_client.get_pr_diff')
    @patch('src.utils.openai_client.analyze_code_with_ai')
    @patch('src.utils.bitbucket_client.post_comment_to_pr')
    def test_webhook_successful_processing(self, mock_post_comment, mock_analyze, 
                                         mock_get_diff, mock_extract_pr, 
                                         mock_is_pr_event, mock_verify, 
                                         client, sample_webhook_payload, sample_diff):
        """Test successful webhook processing"""
        # Mock all dependencies
        def mock_decorator(f):
            return f
        mock_verify.return_value = mock_decorator
        
        mock_is_pr_event.return_value = True
        mock_extract_pr.return_value = {
            'id': 123,
            'title': 'Test PR',
            'repository': {'full_name': 'test/repo'}
        }
        mock_get_diff.return_value = sample_diff
        mock_analyze.return_value = {
            'overall_comment': 'Good changes overall',
            'file_comments': [],
            'documentation': []
        }
        mock_post_comment.return_value = True
        
        response = client.post('/webhook',
                             data=json.dumps(sample_webhook_payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['pr_id'] == 123
    
    def test_rate_limiting(self, client, mock_env_vars):
        """Test rate limiting functionality"""
        # Set very low rate limit for testing
        with patch('app.API_RATE_LIMIT', 2):
            # Make requests beyond the limit
            for i in range(3):
                response = client.get('/test')
                if i < 2:
                    assert response.status_code == 200
                else:
                    # Third request should be rate limited
                    assert response.status_code == 429
                    data = json.loads(response.data)
                    assert 'Rate limit exceeded' in data['message']