import os
import logging
import requests
import re
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
GITHUB_API_BASE = "https://api.github.com"


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
                f"{GITHUB_API_BASE}/repos/"
                f"{pr_info['repository']['full_name']}/pulls/"
                f"{pr_info['id']}"
            )
            logger.info(f"Constructed diff URL: {diff_url}")

        # Prepare authentication
        headers = {}

        if not GITHUB_ACCESS_TOKEN:
            logger.error("GITHUB_ACCESS_TOKEN not configured")
            return None

        headers["Authorization"] = f"token {GITHUB_ACCESS_TOKEN}"
        headers["Accept"] = "application/vnd.github.v3.diff"

        # Make the request
        response = requests.get(
            diff_url,
            headers=headers,
            timeout=30
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
    """Post a general comment to the PR (treated as issue comment in GitHub)"""
    try:
        url = (
            f"{GITHUB_API_BASE}/repos/"
            f"{pr_info['repository']['full_name']}/issues/"
            f"{pr_info['id']}/comments"
        )

        # Prepare comment data
        data = {
            "body": f"## AI Code Review\n\n{comment}"
        }

        # Prepare authentication
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json"
        }

        if not GITHUB_ACCESS_TOKEN:
            logger.error("GITHUB_ACCESS_TOKEN not configured")
            return False

        headers["Authorization"] = f"token {GITHUB_ACCESS_TOKEN}"

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
    """Normalize file path for GitHub API compatibility"""
    if not file_path:
        return ""

    # Convert Windows-style paths to forward slashes
    normalized = file_path.replace('\\', '/')

    # Remove leading slash if present
    normalized = normalized.lstrip('/')

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
    """Post an inline comment to a specific line in the PR (review comment)"""
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

        if not file_path:
            logger.error("File path cannot be None")
            return False

        commit_id = pr_info.get("head_sha")
        if not commit_id:
            logger.error("Commit ID (head_sha) is missing in PR info")
            return False

        url = (
            f"{GITHUB_API_BASE}/repos/"
            f"{pr_info['repository']['full_name']}/pulls/"
            f"{pr_info['id']}/comments"
        )

        normalized_path = normalize_path(file_path)

        # Prepare comment data
        # GitHub review comments require commit_id, path, and line/position.
        # Ideally we use 'line' (diff line) but that's tricky.
        # GitHub API v3 allows 'line' which is the line number in the new file.
        data = {
            "body": comment,
            "commit_id": commit_id,
            "path": normalized_path,
            "line": line_number,
            "side": "RIGHT"
        }

        # Prepare authentication
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json"
        }

        if not GITHUB_ACCESS_TOKEN:
            logger.error("GITHUB_ACCESS_TOKEN not configured")
            return False

        headers["Authorization"] = f"token {GITHUB_ACCESS_TOKEN}"

        # Make the request
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code in [200, 201]:
            logger.info(
                f"Successfully posted inline comment to PR {pr_info['id']} "
                f"at {normalized_path}:{line_number}"
            )
            return True
        else:
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

def get_file_content(pr_info, file_path):
    """Get content of a file from the repository"""
    try:
        repo_full_name = pr_info['repository']['full_name']
        ref = pr_info.get('source_branch', 'main')

        url = (
            f"{GITHUB_API_BASE}/repos/"
            f"{repo_full_name}/contents/{file_path}"
        )

        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if not GITHUB_ACCESS_TOKEN:
            logger.error("GITHUB_ACCESS_TOKEN not configured")
            return None

        headers["Authorization"] = f"token {GITHUB_ACCESS_TOKEN}"

        params = {'ref': ref}

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code == 404:
            logger.info(f"File {file_path} not found in repo")
            return None

        response.raise_for_status()

        content_data = response.json()
        if 'content' in content_data and content_data.get('encoding') == 'base64':
            return base64.b64decode(content_data['content']).decode('utf-8')

        return None

    except Exception as e:
        logger.warning(f"Error getting file content for {file_path}: {str(e)}")
        return None
