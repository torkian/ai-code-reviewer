import os
import re
import logging
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import utility modules
from src.utils.webhook_utils import verify_webhook_signature, is_pull_request_event, extract_pr_info
from src.utils.bitbucket_client import (
    get_pr_diff, 
    post_comment_to_pr, 
    post_inline_comment_to_pr, 
    extract_files_from_diff
)
from src.utils.openai_client import analyze_code_with_ai

# Set up logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"ai_reviewer_{datetime.datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "60"))  # requests per hour

# Initialize Flask app
app = Flask(__name__)

# Dictionary to track request counts for rate limiting
request_counts = {}

def rate_limit(f):
    """Decorator to implement rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
            
        client_ip = request.remote_addr
        current_time = datetime.datetime.now()
        hour_key = current_time.strftime('%Y-%m-%d-%H')
        
        # Initialize or update request count for this IP
        if client_ip not in request_counts:
            request_counts[client_ip] = {}
        
        if hour_key not in request_counts[client_ip]:
            # Clean up old entries
            request_counts[client_ip] = {hour_key: 0}
        
        # Increment count
        request_counts[client_ip][hour_key] += 1
        count = request_counts[client_ip][hour_key]
        
        # Check if over limit
        if count > API_RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for {client_ip}: {count} requests in the current hour")
            return jsonify({
                "status": "error", 
                "message": f"Rate limit exceeded. Maximum {API_RATE_LIMIT} requests per hour."
            }), 429
            
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET"])
def home():
    return "Bitbucket AI Code Reviewer is running!"
    
@app.route("/test", methods=["GET"])
def test():
    logger.info("Test endpoint accessed")
    return jsonify({
        "status": "success",
        "message": "Server is accessible",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/webhook", methods=["POST"])
@verify_webhook_signature
@rate_limit
def webhook():
    # Parse the webhook payload
    payload = request.json
    client_ip = request.remote_addr
    
    # Log the incoming webhook
    logger.info(f"Received webhook from {client_ip}")
    
    # Check if this is a pull request event
    if not is_pull_request_event(payload, request.headers):
        logger.info("Ignoring non-PR event")
        return jsonify({"status": "ignored", "message": "Not a PR event"}), 200
    
    # Extract PR information
    pr_info = extract_pr_info(payload)
    logger.info(f"Processing PR #{pr_info['id']}: {pr_info['title']} from repo {pr_info['repository']['full_name']}")
    
    # Get the diff for the PR
    diff = get_pr_diff(pr_info)
    if not diff:
        logger.error("Failed to retrieve PR diff")
        return jsonify({"status": "error", "message": "Failed to retrieve PR diff"}), 500
        
    logger.info(f"Retrieved diff with {len(diff)} characters")
    
    # Extract actual files from the diff for validation
    actual_files = extract_files_from_diff(diff)
    logger.info(f"Found {len(actual_files)} files in diff: {', '.join(actual_files[:5])}")
    
    # Analyze the code with AI
    logger.info("Starting AI code analysis")
    analysis = analyze_code_with_ai(diff)
    logger.info("AI analysis completed")
    
    # Post comments to the PR
    logger.info("Posting comments to Bitbucket PR")
    
    # Post overall comment
    if "overall_comment" in analysis:
        post_comment_to_pr(pr_info, analysis["overall_comment"])
    
    # Collect any inline comments that fail
    failed_comments = []
    
    # Post file-specific comments
    for comment in analysis.get("file_comments", []):
        if "file" in comment and "line_number" in comment and "comment" in comment:
            file_path = comment["file"]
            line_number = comment["line_number"]
            
            # Get comment text
            comment_text = comment["comment"]
            
            # Add category prefix if available
            if "category" in comment:
                category = comment["category"].upper()
                comment_text = f"[{category}] {comment_text}"
                
            # Ensure code blocks have language specification if missing
            if "```" in comment_text and not re.search(r"```\w+", comment_text):
                # Try to detect language from file extension
                file_ext = os.path.splitext(file_path)[1].lower()
                lang = ""
                
                if file_ext in ['.py', '.pyw']:
                    lang = 'python'
                elif file_ext in ['.js', '.jsx']:
                    lang = 'javascript'
                elif file_ext in ['.ts', '.tsx']:
                    lang = 'typescript'
                elif file_ext in ['.html', '.htm']:
                    lang = 'html'
                elif file_ext in ['.css']:
                    lang = 'css'
                elif file_ext in ['.java']:
                    lang = 'java'
                elif file_ext in ['.c', '.cpp', '.cc', '.h', '.hpp']:
                    lang = 'cpp'
                elif file_ext in ['.rb']:
                    lang = 'ruby'
                elif file_ext in ['.go']:
                    lang = 'go'
                elif file_ext in ['.php']:
                    lang = 'php'
                
                if lang:
                    comment_text = comment_text.replace("```\n", f"```{lang}\n")
            
            # Attempt to post the inline comment
            logger.info(f"Posting inline comment for file: {file_path}, line: {line_number}")
            result = post_inline_comment_to_pr(pr_info, file_path, line_number, comment_text)
            
            # If inline comment fails, add it to the list for a fallback comment
            if not result:
                logger.warning(f"Failed to post inline comment, adding to fallback list")
                failed_comments.append({
                    "file": file_path,
                    "line": line_number,
                    "category": comment.get("category", "general"),
                    "comment": comment_text
                })
    
    # Post documentation suggestions
    for doc in analysis.get("documentation", []):
        if "file" in doc and "line_number" in doc and "doc_comment" in doc:
            file_path = doc["file"]
            line_number = doc["line_number"]
            
            # Format the documentation with better markdown
            doc_comment = doc['doc_comment']
            
            # Detect language from file extension for better code formatting
            file_ext = os.path.splitext(file_path)[1].lower()
            lang = ""
            if file_ext in ['.py', '.pyw']:
                lang = 'python'
            elif file_ext in ['.js', '.jsx']:
                lang = 'javascript'
            elif file_ext in ['.ts', '.tsx']:
                lang = 'typescript'
            elif file_ext in ['.java']:
                lang = 'java'
            elif file_ext in ['.c', '.cpp', '.cc', '.h', '.hpp']:
                lang = 'cpp'
            else:
                lang = 'text'
                
            # Format the documentation comment
            doc_text = f"**Suggested Documentation:**\n```{lang}\n{doc_comment}\n```"
            
            # Attempt to post the inline comment
            logger.info(f"Posting documentation suggestion for file: {file_path}, line: {line_number}")
            result = post_inline_comment_to_pr(pr_info, file_path, line_number, doc_text)
            
            # If inline comment fails, add it to the list for a fallback comment
            if not result:
                logger.warning(f"Failed to post documentation suggestion, adding to fallback list")
                failed_comments.append({
                    "file": file_path,
                    "line": line_number,
                    "category": "documentation",
                    "comment": doc_text
                })
    
    # Post a fallback comment with all the failed inline comments
    if failed_comments:
        logger.info(f"Posting fallback comment with {len(failed_comments)} failed inline comments")
        fallback_text = "## Inline Comments (Could not post directly)\n\n"
        
        # Add all comments without categories
        for comment in failed_comments:
            fallback_text += f"**{comment['file']} (line {comment['line']}):**\n{comment['comment']}\n\n---\n\n"
            
        post_comment_to_pr(pr_info, fallback_text)
    
    logger.info("PR processing complete")
    
    # Return response
    return jsonify({
        "status": "success",
        "message": "PR analyzed and comments posted",
        "pr_id": pr_info["id"],
        "repo": pr_info["repository"]["full_name"]
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    logger.info(f"Starting server on port {port}, debug={debug}")
    app.run(debug=debug, host="0.0.0.0", port=port)