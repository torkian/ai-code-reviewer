import yaml
import logging
import fnmatch
import re

logger = logging.getLogger(__name__)

def parse_repo_config(content):
    """
    Parse repository configuration from YAML content
    """
    if not content:
        return {}

    try:
        config = yaml.safe_load(content)
        if not isinstance(config, dict):
            logger.warning("Config file is not a dictionary")
            return {}
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {str(e)}")
        return {}

def filter_diff(diff_content, ignore_patterns):
    """
    Filter out files from diff content that match ignore patterns
    """
    if not diff_content or not ignore_patterns:
        return diff_content

    filtered_chunks = []

    # Split diff by "diff --git"
    # The first element might be empty or contain preamble
    chunks = re.split(r'(^diff --git .*$)', diff_content, flags=re.MULTILINE)

    # chunks[0] is usually empty or preamble
    if chunks[0].strip():
        filtered_chunks.append(chunks[0])

    # Iterate through pairs of (header, body)
    # split keeps the delimiter, so we get [preamble, header1, body1, header2, body2...]
    # But checking split output:
    # 'a\nb'.split('\n') -> ['a', 'b']
    # re.split with group returns the separator too.

    # Let's iterate from index 1
    for i in range(1, len(chunks), 2):
        header = chunks[i]
        body = chunks[i+1] if i+1 < len(chunks) else ""

        # Extract filename from header
        # Header format: diff --git a/path/to/file b/path/to/file
        match = re.search(r'diff --git a/(.*?) b/(.*?)$', header)
        if match:
            file_path = match.group(2) # Use target path

            # Check if file matches any ignore pattern
            should_ignore = False
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    should_ignore = True
                    break

            if not should_ignore:
                filtered_chunks.append(header + body)
            else:
                logger.info(f"Filtering out ignored file: {file_path}")
        else:
            # Could not parse header, keep it to be safe
            filtered_chunks.append(header + body)

    return "".join(filtered_chunks)
