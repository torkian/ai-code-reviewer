"""
Tests for GitHub API client
"""
import requests
from unittest.mock import patch, MagicMock
from src.utils.github_client import (
    get_pr_diff,
    post_comment_to_pr,
    post_inline_comment_to_pr,
    extract_files_from_diff,
    normalize_path
)


class TestGithubClient:
    """Test cases for GitHub API client functions"""

    def test_normalize_path(self):
        """Test path normalization"""
        # Test normal paths
        assert normalize_path("src/test.py") == "src/test.py"
        assert normalize_path("/src/test.py") == "src/test.py"
        assert normalize_path("src\\test.py") == "src/test.py"

        # Test edge cases
        assert normalize_path("") == ""
        assert normalize_path("/") == ""

        # Invalid but handled
        assert normalize_path("../test.py") == "../test.py"

    def test_extract_files_from_diff(self, sample_diff):
        """Test file extraction from diff"""
        files = extract_files_from_diff(sample_diff)
        assert "test.py" in files

        # Test empty diff
        assert extract_files_from_diff("") == []
        assert extract_files_from_diff(None) == []

    @patch('src.utils.github_client.GITHUB_ACCESS_TOKEN', 'test-token')
    @patch('requests.get')
    def test_get_pr_diff_success(self, mock_get, sample_github_webhook_payload, sample_diff):
        """Test successful PR diff retrieval"""
        # Prepare mock info from payload
        from src.utils.webhook_utils import extract_pr_info
        pr_info = extract_pr_info(sample_github_webhook_payload)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_diff
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_pr_diff(pr_info)

        assert result == sample_diff
        mock_get.assert_called_once()

        # Verify authorization header
        call_args = mock_get.call_args
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'token test-token'
        assert headers['Accept'] == 'application/vnd.github.v3.diff'

    @patch('src.utils.github_client.GITHUB_ACCESS_TOKEN', None)
    def test_get_pr_diff_no_token(self, sample_github_webhook_payload):
        """Test PR diff retrieval without token"""
        from src.utils.webhook_utils import extract_pr_info
        pr_info = extract_pr_info(sample_github_webhook_payload)

        result = get_pr_diff(pr_info)
        assert result is None

    @patch('src.utils.github_client.GITHUB_ACCESS_TOKEN', 'test-token')
    @patch('requests.post')
    def test_post_comment_success(self, mock_post, sample_github_webhook_payload):
        """Test successful comment posting"""
        from src.utils.webhook_utils import extract_pr_info
        pr_info = extract_pr_info(sample_github_webhook_payload)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = post_comment_to_pr(pr_info, "Test comment")

        assert result is True
        mock_post.assert_called_once()

        # Verify request data
        call_args = mock_post.call_args
        data = call_args[1]['json']
        assert 'body' in data
        assert 'AI Code Review' in data['body']

    @patch('src.utils.github_client.GITHUB_ACCESS_TOKEN', 'test-token')
    @patch('requests.post')
    def test_post_inline_comment_success(self, mock_post, sample_github_webhook_payload):
        """Test successful inline comment posting"""
        from src.utils.webhook_utils import extract_pr_info
        pr_info = extract_pr_info(sample_github_webhook_payload)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = post_inline_comment_to_pr(
            pr_info,
            "src/test.py",
            10,
            "This line needs improvement"
        )

        assert result is True
        mock_post.assert_called_once()

        # Verify inline comment structure
        call_args = mock_post.call_args
        data = call_args[1]['json']
        assert data['path'] == 'src/test.py'
        assert data['line'] == 10
        assert data['side'] == 'RIGHT'
        assert data['commit_id'] == 'abc123def456'

    @patch('src.utils.github_client.GITHUB_ACCESS_TOKEN', 'test-token')
    def test_post_inline_comment_no_commit_id(self):
        """Test inline comment without commit ID"""
        pr_info = {'id': 123, 'repository': {'full_name': 'test/repo'}} # Missing head_sha

        result = post_inline_comment_to_pr(
            pr_info,
            "src/test.py",
            10,
            "Test comment"
        )

        assert result is False
