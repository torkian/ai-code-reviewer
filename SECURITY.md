# Security Recommendations

This document outlines security recommendations for deploying the Bitbucket AI Reviewer service.

## Current Security Features

The application includes several security features:

1. **Webhook Signature Verification**
   - Uses HMAC-SHA256 to verify that webhook requests come from Bitbucket
   - Requires a shared secret between Bitbucket and this service

2. **Rate Limiting**
   - Limits requests per IP address to prevent abuse
   - Configurable via the `API_RATE_LIMIT` environment variable

3. **Secure Logging**
   - Detailed logs for monitoring and auditing
   - No sensitive data is logged

## Additional Deployment Recommendations

For production deployment, consider these additional security measures:

### 1. Deploy Behind a Reverse Proxy

- Use Nginx or Apache as a reverse proxy
- Configure TLS/SSL for HTTPS
- Set up proper headers (Content-Security-Policy, X-Frame-Options, etc.)

Example Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name your-reviewer-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'";
    add_header X-Content-Type-Options "nosniff";

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Use a Firewall

- Configure a firewall to allow only necessary connections
- Whitelist Bitbucket webhook IP addresses if possible
- Example using `ufw` (Uncomplicated Firewall):
  ```
  ufw allow from bitbucket-ip-range to any port 443 proto tcp
  ```

### 3. Run as Non-Root User

- Create a dedicated user for the service
- Never run the service as root
- Example:
  ```
  useradd -m -s /bin/bash reviewer
  # Run application as this user
  su - reviewer -c "cd /path/to/app && python app.py"
  ```

### 4. Use Environment Variables Securely

- Store sensitive values in environment variables
- Consider using a secrets management service in production
- Never hardcode secrets in the application code

### 5. Regular Updates

- Keep dependencies updated to address security vulnerabilities
- Run `pip install --upgrade -r requirements.txt` regularly

### 6. Monitoring and Logging

- Set up monitoring for the service
- Consider forwarding logs to a central logging system
- Monitor for unusual patterns or potential security issues

## Setting Up Webhook Secret in Bitbucket

1. Generate a strong random secret:
   ```
   openssl rand -hex 32
   ```

2. Add this secret to your `.env` file:
   ```
   WEBHOOK_SECRET=your_generated_secret
   ```

3. Configure the same secret in Bitbucket:
   - Go to your repository > Settings > Webhooks
   - Edit your webhook
   - Enter the same secret in the "Secret" field