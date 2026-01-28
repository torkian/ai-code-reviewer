import pytest
from src.utils.config_utils import parse_repo_config, filter_diff

def test_parse_repo_config_valid_yaml():
    content = """
    ignore_files:
      - "*.json"
      - "tests/*"
    extra_instructions: "Focus on security."
    """
    config = parse_repo_config(content)
    assert config['ignore_files'] == ['*.json', 'tests/*']
    assert config['extra_instructions'] == 'Focus on security.'

def test_parse_repo_config_invalid_yaml():
    content = "invalid: [ yaml: {"
    config = parse_repo_config(content)
    assert config == {}

def test_parse_repo_config_empty():
    assert parse_repo_config("") == {}
    assert parse_repo_config(None) == {}

def test_filter_diff_no_patterns():
    diff = "diff --git a/file.py b/file.py\n..."
    assert filter_diff(diff, []) == diff
    assert filter_diff(diff, None) == diff

def test_filter_diff_filter_match():
    diff = """diff --git a/file.py b/file.py
index 123..456 100644
--- a/file.py
+++ b/file.py
@@ -1 +1 @@
-old
+new
diff --git a/test.json b/test.json
index 789..abc 100644
--- a/test.json
+++ b/test.json
@@ -1 +1 @@
-{}
+[]
"""
    filtered = filter_diff(diff, ['*.json'])
    assert 'file.py' in filtered
    assert 'test.json' not in filtered

def test_filter_diff_multiple_patterns():
    diff = """diff --git a/src/main.py b/src/main.py
...
diff --git a/tests/test_main.py b/tests/test_main.py
...
diff --git a/config.json b/config.json
...
"""
    filtered = filter_diff(diff, ['tests/*', '*.json'])
    assert 'src/main.py' in filtered
    assert 'tests/test_main.py' not in filtered
    assert 'config.json' not in filtered
