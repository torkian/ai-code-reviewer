import os
import logging
import requests
import re
import json

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
BITBUCKET_ACCESS_TOKEN = os.getenv("BITBUCKET_ACCESS_TOKEN")
BITBUCKET_API_BASE = "https://api.bitbucket.org/2.0"


def get_pr_diff(pr_info):
    """Get the diff content from a pull request"""
    try:
        # Get diff URL from PR info if available
        diff_url = None
        if 'links' in pr_info and 'diff' in pr_info['links']:
            diff_url = pr_info['links']['diff']['href']
            logger.info(f"Using diff URL from PR links: {diff_url}")
        else:
            # Fallback to constructing the URL
            diff_url = (
                f"{BITBUCKET_API_BASE}/repositories/"
                f"{pr_info['repository']['full_name']}/pullrequests/"
                f"{pr_info['id']}/diff"
            )
            logger.info(f"Constructed diff URL: {diff_url}")

        # Prepare authentication
        headers = {}

        if not BITBUCKET_ACCESS_TOKEN:
            logger.error("BITBUCKET_ACCESS_TOKEN not configured")
            return None

        headers["Authorization"] = f"Bearer {BITBUCKET_ACCESS_TOKEN}"

        headers["Accept"] = "text/plain"

        # Make the request
        response = requests.get(
            diff_url,
            headers=headers,
            timeout=30  # Increased timeout for large diffs
        )
        response.raise_for_status()

        diff_content = response.text
        logger.info(
            f"Successfully retrieved diff ({len(diff_content)} characters)"
        )

        # Truncate very large diffs to avoid OpenAI token limits
        max_diff_size = 20000
        if len(diff_content) > max_diff_size:
            logger.warning(
                f"Diff is very large ({len(diff_content)} chars), "
                f"truncating to {max_diff_size} chars"
            )
            diff_content = (
                diff_content[:max_diff_size] +
                f"\n... [Diff truncated, total size: "
                f"{len(diff_content)} chars]"
            )

        return diff_content
    except Exception as e:
        logger.error(f"Error getting PR diff: {str(e)}")
        return None


def post_comment_to_pr(pr_info, comment):
    """Post a general comment to the PR"""
    try:
        url = (
            f"{BITBUCKET_API_BASE}/repositories/"
            f"{pr_info['repository']['full_name']}/pullrequests/"
            f"{pr_info['id']}/comments"
        )

        # Prepare comment data
        data = {
            "content": {
                "raw": f"## AI Code Review\n\n{comment}"
            }
        }

        # Prepare authentication
        headers = {"Content-Type": "application/json"}

        if not BITBUCKET_ACCESS_TOKEN:
            logger.error("BITBUCKET_ACCESS_TOKEN not configured")
            return False

        headers["Authorization"] = f"Bearer {BITBUCKET_ACCESS_TOKEN}"

        # Make the request
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()
        logger.info(f"Successfully posted comment to PR {pr_info['id']}")
        return True
    except Exception as e:
        logger.error(f"Error posting comment to PR: {str(e)}")
        return False


def normalize_path(file_path):
    """Normalize file path for Bitbucket API compatibility"""
    if not file_path:
        return ""

    # Convert Windows-style paths to forward slashes
    normalized = file_path.replace('\\', '/')

    # Remove leading slash if present (Bitbucket doesn't want absolute paths)
    normalized = normalized.lstrip('/')

    # Validate path (should be relative within repo)
    if not normalized or normalized.startswith('..'):
        logger.warning(
            f"Invalid path format: {file_path}, normalized to: {normalized}"
        )

    return normalized


def extract_files_from_diff(diff_content):
    """Extract file names from diff content"""
    if not diff_content:
        return []

    # Match file paths in diff headers
    matches = re.findall(
        r'diff --git a/(.*?) b/(.*?)$', diff_content, re.MULTILINE
    )

    # Return the target (b) files
    return [b for _, b in matches] if matches else []


def post_inline_comment_to_pr(pr_info, file_path, line_number, comment):
    """Post an inline comment to a specific line in the PR"""
    try:
        # Validate inputs
        if not isinstance(line_number, int):
            try:
                line_number = int(line_number)
            except (ValueError, TypeError):
                logger.error(
                    f"Invalid line number: {line_number} - must be an integer"
                )
                return False

        # Ensure file_path is not None
        if file_path is None:
            logger.error("File path cannot be None")
            return False

        url = (
            f"{BITBUCKET_API_BASE}/repositories/"
            f"{pr_info['repository']['full_name']}/pullrequests/"
            f"{pr_info['id']}/comments"
        )

        # Normalize the file path to make it compatible with Bitbucket
        normalized_path = normalize_path(file_path)
        logger.info(
            f"Normalized path from '{file_path}' to '{normalized_path}'"
        )

        if not normalized_path:
            logger.error(f"Invalid file path: {file_path}")
            return False

        # Prepare authentication
        headers = {"Content-Type": "application/json"}

        if not BITBUCKET_ACCESS_TOKEN:
            logger.error("BITBUCKET_ACCESS_TOKEN not configured")
            return False

        headers["Authorization"] = f"Bearer {BITBUCKET_ACCESS_TOKEN}"

        # Based on our test results, we found that this repo doesn't support
        # commit_id
        # Use the format without commit_id that worked in our tests
        data = {
            "content": {"raw": comment},
            "inline": {
                "path": normalized_path,
                "to": line_number
            }
        }

        # Log the request for debugging
        logger.info(f"Posting inline comment with data: {json.dumps(data)}")

        # Make the request
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        # Check if successful
        if response.status_code == 200 or response.status_code == 201:
            logger.info(
                f"Successfully posted inline comment to PR {pr_info['id']} "
                f"at {normalized_path}:{line_number}"
            )
            return True
        else:
            # Log the error for debugging
            error_detail = (
                response.json() if response.text else "No error details"
            )
            logger.error(
                f"Failed to post inline comment: {response.status_code} - "
                f"{error_detail}"
            )
            return False

    except Exception as e:
        logger.error(f"Error posting inline comment to PR: {str(e)}")
        return False


def get_latest_commit_id(pr_info):
    """Get the latest commit ID in the PR"""
    try:
        url = (
            f"{BITBUCKET_API_BASE}/repositories/"
            f"{pr_info['repository']['full_name']}/pullrequests/"
            f"{pr_info['id']}/commits"
        )

        # Prepare authentication
        headers = {}

        if not BITBUCKET_ACCESS_TOKEN:
            logger.error("BITBUCKET_ACCESS_TOKEN not configured")
            return None

        headers["Authorization"] = f"Bearer {BITBUCKET_ACCESS_TOKEN}"

        # Make the request
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        commits = response.json().get("values", [])
        if commits:
            commit_id = commits[0].get("hash")
            logger.info(f"Retrieved latest commit ID: {commit_id}")
            return commit_id
        else:
            logger.warning("No commits found in the PR")
            return None
    except Exception as e:
        logger.error(f"Error getting latest commit ID: {str(e)}")
        return None
