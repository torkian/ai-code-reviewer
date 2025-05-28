"""
Tests for Bitbucket API client
"""
import pytest
import requests
from unittest.mock import patch, MagicMock
from src.utils.bitbucket_client import (
    get_pr_diff, 
    post_comment_to_pr, 
    post_inline_comment_to_pr,
    extract_files_from_diff,
    normalize_path
)


class TestBitbucketClient:
    """Test cases for Bitbucket API client functions"""
    
    def test_normalize_path(self):
        """Test path normalization"""
        # Test normal paths
        assert normalize_path("src/test.py") == "src/test.py"
        assert normalize_path("/src/test.py") == "src/test.py"
        assert normalize_path("src\\test.py") == "src/test.py"
        
        # Test edge cases
        assert normalize_path("") == ""
        assert normalize_path("/") == ""
        assert normalize_path("../test.py") == "../test.py"  # Invalid but handled
    
    def test_extract_files_from_diff(self, sample_diff):
        """Test file extraction from diff"""
        files = extract_files_from_diff(sample_diff)
        assert "test.py" in files
        
        # Test empty diff
        assert extract_files_from_diff("") == []
        assert extract_files_from_diff(None) == []
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', 'test-token')
    @patch('requests.get')
    def test_get_pr_diff_success(self, mock_get, sample_pr_info, sample_diff):
        """Test successful PR diff retrieval"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_diff
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_pr_diff(sample_pr_info)
        
        assert result == sample_diff
        mock_get.assert_called_once()
        
        # Verify authorization header
        call_args = mock_get.call_args
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test-token'
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', None)
    def test_get_pr_diff_no_token(self, sample_pr_info):
        """Test PR diff retrieval without token"""
        result = get_pr_diff(sample_pr_info)
        assert result is None
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', 'test-token')
    @patch('requests.get')
    def test_get_pr_diff_api_error(self, mock_get, sample_pr_info):
        """Test PR diff retrieval with API error"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = get_pr_diff(sample_pr_info)
        assert result is None
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', 'test-token')
    @patch('requests.post')
    def test_post_comment_success(self, mock_post, sample_pr_info):
        """Test successful comment posting"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = post_comment_to_pr(sample_pr_info, "Test comment")
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verify request data
        call_args = mock_post.call_args
        data = call_args[1]['json']
        assert 'content' in data
        assert 'AI Code Review' in data['content']['raw']
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', None)
    def test_post_comment_no_token(self, sample_pr_info):
        """Test comment posting without token"""
        result = post_comment_to_pr(sample_pr_info, "Test comment")
        assert result is False
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', 'test-token')
    @patch('requests.post')
    def test_post_inline_comment_success(self, mock_post, sample_pr_info):
        """Test successful inline comment posting"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = post_inline_comment_to_pr(
            sample_pr_info, 
            "src/test.py", 
            10, 
            "This line needs improvement"
        )
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verify inline comment structure
        call_args = mock_post.call_args
        data = call_args[1]['json']
        assert 'inline' in data
        assert data['inline']['path'] == 'src/test.py'
        assert data['inline']['to'] == 10
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', 'test-token')
    @patch('requests.post')
    def test_post_inline_comment_invalid_line(self, mock_post, sample_pr_info):
        """Test inline comment with invalid line number"""
        result = post_inline_comment_to_pr(
            sample_pr_info, 
            "src/test.py", 
            "invalid", 
            "Test comment"
        )
        
        assert result is False
        mock_post.assert_not_called()
    
    @patch('src.utils.bitbucket_client.BITBUCKET_ACCESS_TOKEN', 'test-token')
    def test_post_inline_comment_none_file(self, sample_pr_info):
        """Test inline comment with None file path"""
        result = post_inline_comment_to_pr(
            sample_pr_info, 
            None, 
            10, 
            "Test comment"
        )
        
        assert result is False