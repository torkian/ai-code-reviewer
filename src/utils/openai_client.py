import os
import json
import logging
import requests

# Configure logging
logger = logging.getLogger(__name__)


def call_openai_api(prompt, system_message=None):
    """
    Direct HTTP call to OpenAI API instead of using the client library
    This avoids proxy issues and other configuration problems
    """
    try:
        # Get API key from environment
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

        # Check if API key is configured
        if not OPENAI_API_KEY:
            logger.error("OpenAI API key not configured")
            return (
                "Error: OpenAI API key not configured. Please set "
                "OPENAI_API_KEY environment variable."
            )

        logger.info("Preparing OpenAI API call...")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        # Default system message if none provided
        if not system_message:
            system_message = "You are a code review assistant. Analyze the code diff provided and give constructive feedback, highlighting potential issues, suggesting improvements, and commenting on code quality."

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        logger.info("Sending request to OpenAI API...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120  # Increased timeout
        )

        logger.info(f"OpenAI API response status: {response.status_code}")

        # Handle different status codes explicitly
        if response.status_code != 200:
            error_info = (
                response.json() if response.text else "No error details available"
            )
            logger.error(
                f"OpenAI API error: {response.status_code} - {error_info}"
            )
            return (
                f"Error: The AI service returned an error "
                f"(HTTP {response.status_code}). Please check the logs "
                "for details."
            )

        response_data = response.json()
        logger.info("Successfully parsed OpenAI response")

        if 'choices' in response_data and len(response_data['choices']) > 0:
            content = response_data['choices'][0]['message']['content']
            logger.info(
                f"Successfully extracted content ({len(content)} chars)"
            )
            return content
        else:
            logger.error(f"Unexpected OpenAI response format: {response_data}")
            return "Error: Unexpected response format from AI service."

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to OpenAI API: {str(e)}")
        return (
            "Error: Could not connect to the AI service. Please check "
            "your internet connection and try again."
        )
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout calling OpenAI API: {str(e)}")
        return (
            "Error: The AI service request timed out. Please try again "
            "later."
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from OpenAI response: {str(e)}")
        return (
            "Error: Could not parse the AI service response. "
            "Please check the logs."
        )
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return f"Error calling AI service: {str(e)}"


def analyze_code_with_ai(diff):
    """
    Analyze code diff using OpenAI API and return structured analysis
    """
    if not diff:
        logger.warning("No diff content provided for analysis")
        return {"overall_comment": "No changes found to analyze."}

    # Log diff size
    diff_size_kb = len(diff) / 1024
    logger.info(f"Analyzing diff of size: {diff_size_kb:.2f} KB")

    # Handle large diffs
    if diff_size_kb > 50:
        logger.warning(f"Diff is extremely large ({diff_size_kb:.2f} KB). Providing a simplified analysis.")
        return {
            "overall_comment": "This pull request contains a very large number of changes (over 50KB). For best results, consider breaking down large changes into smaller, more focused pull requests.",
            "file_comments": [],
            "documentation": []
        }

    # Prepare a prompt that emphasizes the need for JSON output
    prompt = f"""
    Perform an expert-level code review on the following diff. Focus specifically on these key areas:

    1. CODE QUALITY:
       - Identify non-idiomatic code patterns
       - Flag code complexity, duplications, or hard-to-maintain patterns
       - Suggest cleaner alternatives following language best practices

    2. BUGS & LOGIC ISSUES:
       - Identify potential runtime errors, edge cases, or logical flaws
       - Look for incorrect error handling or missing validation
       - Pay special attention to asynchronous operations, state management & error propagation

    3. SECURITY VULNERABILITIES:
       - Flag any security issues such as injection risks, unvalidated inputs, or insecure API usage
       - Look for insecure default configurations or leaked credentials
       - Identify potential authorization/authentication bypasses

    4. PERFORMANCE OPTIMIZATIONS:
       - Identify inefficient algorithms or data structures
       - Look for unnecessary loops, excessive memory usage, or resource leaks
       - Find redundant operations or computations that could be optimized

    5. DOCUMENTATION & READABILITY:
       - Recommend documentation for complex functions, classes or logic
       - Suggest meaningful variable/function names where they're unclear
       - Note where additional comments would improve understanding

    ```diff
    {diff}
    ```

    IMPORTANT: Format your response as JSON with the following fields:
    - overall_comment: A thorough summary of the changes covering their purpose, quality, and key concerns
    - file_comments: A list of objects with "file", "line_number", "category" (one of: "quality", "bug", "security", "performance", "documentation"), and "comment" for specific issues
    - documentation: A list of objects with "file", "line_number", and "doc_comment" for suggested documentation

    Example response format:
    ```json
    {{
      "overall_comment": "This PR adds error handling to the user service with generally good practices. There are two potential security issues with input validation and one performance optimization opportunity in the error processing function.",

      "file_comments": [
        {{
          "file": "user_service.py",
          "line_number": 42,
          "category": "security",
          "comment": "This input is used in a database query without validation, creating potential **SQL injection risk**. Consider using parameterized queries: \\n\\n```python\\n# Instead of:\\nuser_id = request.params.get('id')\\nquery = f\\\"SELECT * FROM users WHERE id = {{user_id}}\\\"\\n\\n# Use this:\\nuser_id = request.params.get('id')\\nquery = \\\"SELECT * FROM users WHERE id = %s\\\"\\ncursor.execute(query, (user_id,))\\n```\\n\\nThis prevents attackers from injecting malicious SQL code through the parameter."
        }},

        {{
          "file": "error_handler.js",
          "line_number": 157,
          "category": "performance",
          "comment": "This operation iterates through the entire error list on each validation, resulting in O(n²) complexity. Use a map/dictionary for O(1) lookups:\\n\\n```javascript\\n// Instead of:\\nconst error = errorList.find(e => e.code === errorCode);\\n\\n// Use this:\\nconst errorMap = errorList.reduce((map, error) => {{\\n  map[error.code] = error;\\n  return map;\\n}}, {{}});\\nconst error = errorMap[errorCode];\\n```\\n\\nThis is particularly important for large error lists or frequent lookups."
        }}
      ],

      "documentation": [
        {{
          "file": "user_service.py",
          "line_number": 15,
          "doc_comment": "/**\\n * Gets a user by ID from the database\\n * \\n * @param {{string}} id - The unique user identifier\\n * @returns {{Promise<User>}} The user object or null if not found\\n * @throws {{DatabaseError}} If connection fails\\n */"
        }}
      ]
    }}
    ```

    Be specific and detailed in your comments, including rationale for why issues matter and clear recommendations on how to address them.
    """

    system_message = """You are a senior software engineer with extensive expertise in code quality, security, and performance optimization. Your task is to provide thorough, expert-level code reviews.

IMPORTANT GUIDELINES:
1. Focus on identifying critical issues like security vulnerabilities, performance bottlenecks, logical bugs, and maintainability concerns.
2. Provide specific, actionable feedback that explains both the problem and the recommended solution with appropriate rationale.
3. ALWAYS use proper markdown formatting in your comments:
   - Format code snippets with language-specific code blocks like ```python, ```javascript, etc.
   - Use **bold** for emphasis on important points
   - Use bullet lists for multiple related points
4. For code quality issues, focus on logic, architecture, and best practices.
5. For documentation suggestions, ONLY focus on missing documentation for functions, classes, and complex code blocks.
6. NEVER duplicate the same recommendation in both quality comments and documentation suggestions.
7. Format your response in the required JSON structure exactly as specified.
"""

    try:
        # Call OpenAI API
        response_content = call_openai_api(prompt, system_message)

        # Check if there was an error
        if response_content.startswith("Error:"):
            return {
                "overall_comment": response_content,
                "file_comments": [],
                "documentation": []
            }

        # Extract JSON if content contains markdown code blocks
        if "```json" in response_content:
            json_parts = response_content.split("```json")[1].split("```")[0]
            response_content = json_parts.strip()
        elif "```" in response_content:
            potential_json = response_content.split("```")[1].split("```")[0]
            response_content = potential_json.strip()

        # Parse the JSON content
        try:
            result = json.loads(response_content)
            logger.info("Successfully parsed JSON response from OpenAI")
            return result
        except json.JSONDecodeError as json_err:
            # Fallback if response is not valid JSON
            logger.warning(f"AI response was not in JSON format: {json_err}")
            logger.warning(f"Raw content: {response_content[:500]}...")

            # Create a simplified analysis
            summary = response_content.split("\n\n")[0] if "\n\n" in response_content else response_content[:200]
            return {
                "overall_comment": f"Analysis completed, but the result format was unexpected. Summary: {summary}",
                "file_comments": [],
                "documentation": []
            }
    except Exception as e:
        logger.error(f"Error analyzing code with AI: {str(e)}", exc_info=True)
        return {
            "overall_comment": f"Failed to analyze code due to an error: {str(e)}"
        }
