"""
Tests for OpenAI API client
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from src.utils.openai_client import call_openai_api, analyze_code_with_ai


class TestOpenAIClient:
    """Test cases for OpenAI API client functions"""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('requests.post')
    def test_call_openai_api_success(self, mock_post):
        """Test successful OpenAI API call"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'This is a test response from OpenAI'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = call_openai_api("Test prompt")
        
        assert result == "This is a test response from OpenAI"
        mock_post.assert_called_once()
        
        # Verify API call structure
        call_args = mock_post.call_args
        data = call_args[1]['json']
        assert data['model'] == 'gpt-3.5-turbo'
        assert len(data['messages']) == 2
        assert data['messages'][1]['content'] == "Test prompt"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_call_openai_api_no_key(self):
        """Test OpenAI API call without API key"""
        result = call_openai_api("Test prompt")
        assert "Error: OpenAI API key not configured" in result
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('requests.post')
    def test_call_openai_api_auth_error(self, mock_post):
        """Test OpenAI API call with authentication error"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Invalid API key'}
        mock_post.return_value = mock_response
        
        result = call_openai_api("Test prompt")
        assert "Error: The AI service returned an error (HTTP 401)" in result
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('requests.post')
    def test_call_openai_api_connection_error(self, mock_post):
        """Test OpenAI API call with connection error"""
        mock_post.side_effect = Exception("Connection failed")
        
        result = call_openai_api("Test prompt")
        assert "Error calling AI service" in result
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('src.utils.openai_client.call_openai_api')
    def test_analyze_code_with_ai_success(self, mock_call_api, sample_diff):
        """Test successful code analysis"""
        # Mock successful JSON response
        mock_response = json.dumps({
            "overall_comment": "Good code changes with proper structure",
            "file_comments": [
                {
                    "file": "test.py",
                    "line_number": 3,
                    "category": "quality",
                    "comment": "Consider adding error handling here"
                }
            ],
            "documentation": [
                {
                    "file": "test.py",
                    "line_number": 1,
                    "doc_comment": "/**\n * Function description needed\n */"
                }
            ]
        })
        mock_call_api.return_value = mock_response
        
        result = analyze_code_with_ai(sample_diff)
        
        assert result['overall_comment'] == "Good code changes with proper structure"
        assert len(result['file_comments']) == 1
        assert len(result['documentation']) == 1
        assert result['file_comments'][0]['file'] == 'test.py'
    
    def test_analyze_code_with_ai_no_diff(self):
        """Test code analysis with no diff"""
        result = analyze_code_with_ai("")
        assert result['overall_comment'] == "No changes found to analyze."
    
    def test_analyze_code_with_ai_none_diff(self):
        """Test code analysis with None diff"""
        result = analyze_code_with_ai(None)
        assert result['overall_comment'] == "No changes found to analyze."
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('src.utils.openai_client.call_openai_api')
    def test_analyze_code_with_ai_large_diff(self, mock_call_api):
        """Test code analysis with very large diff"""
        # Create a very large diff (over 50KB)
        large_diff = "diff --git a/test.py b/test.py\n" + "+" + "x" * 60000
        
        result = analyze_code_with_ai(large_diff)
        
        # Should return simplified analysis without calling API
        assert "very large number of changes" in result['overall_comment']
        assert result['file_comments'] == []
        mock_call_api.assert_not_called()
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('src.utils.openai_client.call_openai_api')
    def test_analyze_code_with_ai_invalid_json(self, mock_call_api, sample_diff):
        """Test code analysis with invalid JSON response"""
        mock_call_api.return_value = "This is not valid JSON"
        
        result = analyze_code_with_ai(sample_diff)
        
        assert "Analysis completed, but the result format was unexpected" in result['overall_comment']
        assert result['file_comments'] == []
        assert result['documentation'] == []
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('src.utils.openai_client.call_openai_api')
    def test_analyze_code_with_ai_json_in_markdown(self, mock_call_api, sample_diff):
        """Test code analysis with JSON wrapped in markdown"""
        json_content = {
            "overall_comment": "Test analysis",
            "file_comments": [],
            "documentation": []
        }
        mock_response = f"```json\n{json.dumps(json_content)}\n```"
        mock_call_api.return_value = mock_response
        
        result = analyze_code_with_ai(sample_diff)
        
        assert result['overall_comment'] == "Test analysis"
        assert result['file_comments'] == []
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('src.utils.openai_client.call_openai_api')
    def test_analyze_code_with_ai_error_response(self, mock_call_api, sample_diff):
        """Test code analysis with error response"""
        mock_call_api.return_value = "Error: API rate limit exceeded"
        
        result = analyze_code_with_ai(sample_diff)
        
        assert result['overall_comment'] == "Error: API rate limit exceeded"
        assert result['file_comments'] == []
        assert result['documentation'] == []