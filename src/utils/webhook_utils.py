import os
import hmac
import hashlib
import logging
from functools import wraps
from flask import request, jsonify

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

def verify_webhook_signature(f):
    """Decorator to verify webhook signatures"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip signature check if no secret is configured
        if not WEBHOOK_SECRET:
            logger.warning("Webhook secret not configured - skipping signature verification")
            return f(*args, **kwargs)
            
        # Get the signature from headers (try both variants)
        signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Hub-Signature')
        if not signature:
            logger.warning("No signature found in webhook request")
            return jsonify({"status": "error", "message": "No signature provided"}), 401
            
        # Compute expected signature
        try:
            # Handle prefix if present
            if signature.startswith("sha256="):
                check_signature = signature
                signature_value = signature[7:]  # Remove 'sha256=' prefix
            else:
                check_signature = f"sha256={signature}"
                signature_value = signature
                
            # Compute our signature
            expected_signature = hmac.new(
                WEBHOOK_SECRET.encode('utf-8'),
                request.data,
                hashlib.sha256
            ).hexdigest()
            expected_header = f"sha256={expected_signature}"
            
            # Compare signatures with both formats
            if (hmac.compare_digest(signature_value, expected_signature) or
                hmac.compare_digest(check_signature, expected_header)):
                return f(*args, **kwargs)
            else:
                logger.warning(f"Invalid webhook signature")
                return jsonify({"status": "error", "message": "Invalid signature"}), 401
        except Exception as e:
            logger.error(f"Error validating webhook signature: {str(e)}")
            return jsonify({"status": "error", "message": "Signature validation error"}), 401  
    return decorated_function

def is_pull_request_event(payload, request_headers):
    """Check if the webhook event is related to a PR"""
    try:
        # Log the incoming payload for debugging
        logger.info(f"Webhook payload keys: {list(payload.keys())}")
        
        # Check event key from headers if present in the request
        event_key = request_headers.get('X-Event-Key')
        logger.info(f"X-Event-Key header: {event_key}")
        
        # First check the X-Event-Key header
        if event_key in ["pullrequest:created", "pullrequest:updated"]:
            logger.info(f"Detected PR event from header: {event_key}")
            return True
            
        # Then check payload directly
        if "pullrequest" in payload:
            logger.info("Detected PR event from payload content")
            return True
            
        logger.info("Not a PR event")
        return False
    except Exception as e:
        logger.error(f"Error in PR event detection: {str(e)}", exc_info=True)
        return False

def extract_pr_info(payload):
    """Extract relevant PR information from webhook payload"""
    pullrequest = payload.get("pullrequest", {})
    return {
        "id": pullrequest.get("id"),
        "title": pullrequest.get("title"),
        "source_branch": pullrequest.get("source", {}).get("branch", {}).get("name"),
        "destination_branch": pullrequest.get("destination", {}).get("branch", {}).get("name"),
        "repository": {
            "full_name": pullrequest.get("destination", {}).get("repository", {}).get("full_name"),
        },
        "links": pullrequest.get("links", {}),
    }