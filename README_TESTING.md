# Testing Guide for AI Code Reviewer

This guide explains how to run the comprehensive test suite for the AI Code Reviewer.

## 🧪 Test Suite Overview

The project includes:
- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test complete workflows and API endpoints
- **Anaconda Support**: Works with conda environments
- **Mocked Dependencies**: Tests run without real API calls

## 🚀 Quick Start

### Using Anaconda (Recommended)

```bash
# Create conda environment
conda create -n ai-reviewer python=3.11
conda activate ai-reviewer

# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py
```

### Using Regular Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Or use pytest directly
pytest tests/ -v
```

## 📋 Test Categories

### 1. Unit Tests

Test individual components in isolation:

```bash
# Test Flask application
python run_tests.py tests/test_app.py

# Test Bitbucket client
python run_tests.py tests/test_bitbucket_client.py

# Test OpenAI client
python run_tests.py tests/test_openai_client.py

# Test webhook utilities
python run_tests.py tests/test_webhook_utils.py
```

### 2. Integration Tests

Test the complete application workflow:

```bash
# Run integration tests (starts real Flask server)
python test_integration.py
```

### 3. Installation Verification

Test that your environment is properly configured:

```bash
# Test installation and configuration
python test_installation.py
```

## 🔧 Test Configuration

### Environment Variables for Testing

Tests use mocked environment variables, but you can set real ones for integration tests:

```bash
export OPENAI_API_KEY="sk-your-test-key"
export BITBUCKET_ACCESS_TOKEN="your-test-token"
export WEBHOOK_SECRET="test-secret"
```

### Test Coverage

The test suite covers:

✅ **Flask Application**
- Home and status endpoints
- Webhook endpoint processing
- Rate limiting functionality
- Error handling

✅ **Bitbucket Integration**
- API authentication
- PR diff retrieval
- Comment posting (general and inline)
- Error scenarios

✅ **OpenAI Integration**
- API calls and authentication
- Code analysis functionality
- JSON response parsing
- Error handling

✅ **Webhook Processing**
- Signature verification
- Event type detection
- Payload parsing
- Security features

## 🐛 Debugging Failed Tests

### Common Issues

**1. Import Errors**
```bash
# Make sure you're in the project root
cd /path/to/ai-code-reviewer
python run_tests.py
```

**2. Missing Dependencies**
```bash
# Install test dependencies
pip install pytest pytest-mock
```

**3. Environment Issues**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check package imports
python -c "from src.utils import bitbucket_client"
```

### Verbose Testing

For detailed test output:

```bash
# Very verbose output
pytest tests/ -vv --tb=long

# Show print statements
pytest tests/ -v -s

# Run specific test function
pytest tests/test_app.py::TestFlaskApp::test_home_endpoint -v
```

## 📊 Test Results

### Successful Test Run

```
🧪 AI Code Reviewer Test Suite
==================================================
tests/test_app.py::TestFlaskApp::test_home_endpoint PASSED
tests/test_app.py::TestFlaskApp::test_test_endpoint PASSED
tests/test_bitbucket_client.py::TestBitbucketClient::test_get_pr_diff_success PASSED
...
==================================================
🎉 All tests passed!
```

### Failed Test Example

```
❌ FAILED tests/test_app.py::TestFlaskApp::test_home_endpoint
  AssertionError: assert b'Wrong message' in b'Bitbucket AI Code Reviewer is running!'
```

## 🔄 Continuous Testing

### Pre-commit Testing

Add to your workflow:

```bash
# Before committing changes
python run_tests.py

# Before pushing
python test_integration.py
```

### GitHub Actions (for when you publish)

Create `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: python run_tests.py
    - run: python test_integration.py
```

## 🧩 Adding New Tests

### Test Structure

```python
def test_new_feature():
    """Test description"""
    # Arrange
    input_data = "test input"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == "expected output"
```

### Mocking External APIs

```python
@patch('requests.post')
def test_api_call(mock_post):
    """Test API call with mocked response"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"success": True}
    
    result = call_api()
    assert result is True
```

## 🎯 Test Quality

### Best Practices

- ✅ **Test edge cases** (empty inputs, errors, large data)
- ✅ **Mock external dependencies** (APIs, file system)
- ✅ **Use descriptive test names** that explain what's being tested
- ✅ **Test both success and failure scenarios**
- ✅ **Keep tests independent** (no shared state)

### Coverage Goals

Aim for:
- **90%+ code coverage** for critical functions
- **100% coverage** for security-related code
- **All error paths** tested
- **All API endpoints** tested

---

**Happy Testing! 🧪** Your comprehensive test suite ensures the AI Code Reviewer works reliably in all scenarios.