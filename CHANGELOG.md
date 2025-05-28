# Changelog

## 2025-05-13: Fixed inline comments in Bitbucket PRs

### Fixed
- Fixed 400 Bad Request errors when posting inline comments to Bitbucket PRs
- Updated `post_inline_comment_to_pr` function to work properly with repos that don't accept `commit_id`
- Added path normalization to ensure file paths are in the right format
- Added fallback mechanism in app.py to post comments as regular PR comments if inline comments fail

### Added
- Created diagnostic test scripts to verify the fixes
- Added function to extract file names from PR diffs for better validation
- Improved logging for better error diagnostics

### Changed 
- Simplified `post_inline_comment_to_pr` to use format that works across Bitbucket repositories
- Updated app.py to collect any failed inline comments and post them as a fallback
- Enhanced error handling with more detailed logging

### Technical details
- The specific issue was that the Bitbucket repository's API was rejecting the `commit_id` field in the inline comment payload, resulting in 400 Bad Request errors
- The solution was to remove `commit_id` from the payload completely
- Added validation and normalization for file paths
- Created a fallback mechanism to ensure no comments are lost, even if the inline comment fails