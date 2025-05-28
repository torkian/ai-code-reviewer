# Setup Guide

This guide will walk you through setting up the Bitbucket AI Code Reviewer step by step.

## Step 1: Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher installed
- A Bitbucket account with repository access
- An OpenAI account with API access

## Step 2: Get Required API Keys

### OpenAI API Key

1. Go to [OpenAI API Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Give it a name (e.g., "Bitbucket Code Reviewer")
5. Copy the key - you'll need it for configuration

### Bitbucket Access Token

1. Go to [Bitbucket Account Settings](https://bitbucket.org/account/settings/)
2. Click "App passwords" in the left sidebar
3. Click "Create app password"
4. Give it a label (e.g., "AI Code Reviewer")
5. Select these permissions:
   - **Repositories**: Read
   - **Pull requests**: Read, Write
6. Click "Create"
7. Copy the generated password - you'll need it for configuration

## Step 3: Deploy the Application

### Option A: Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd bitbucket-ai-reviewer
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   BITBUCKET_ACCESS_TOKEN=your-actual-bitbucket-token-here
   WEBHOOK_SECRET=your-chosen-secret-phrase
   PORT=5000
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Test the setup**
   ```bash
   curl http://localhost:5000/test
   ```

### Option B: Docker Deployment

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd bitbucket-ai-reviewer
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Test the deployment**
   ```bash
   curl http://localhost:5000/test
   ```

### Option C: Cloud Deployment (Recommended for Production)

**Heroku (Easiest)**
```bash
# 1. Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
# 2. Deploy your app
heroku login
heroku create your-ai-reviewer-name
heroku config:set OPENAI_API_KEY=your_actual_key
heroku config:set BITBUCKET_ACCESS_TOKEN=your_actual_token  
heroku config:set WEBHOOK_SECRET=your_chosen_secret
git push heroku main
```

**Railway (Modern & Fast)**
```bash
# 1. Install Railway CLI: 
curl -fsSL https://railway.app/install.sh | sh
# 2. Deploy
railway login
railway new
railway link
railway up
# 3. Set environment variables in Railway dashboard
```

**Render (Simple)**
```bash
# 1. Connect your GitHub repo to https://render.com
# 2. Create a new Web Service
# 3. Set environment variables in Render dashboard
# 4. Deploy automatically on every git push
```

**DigitalOcean App Platform**
```bash
# 1. Connect repository at https://cloud.digitalocean.com/apps
# 2. Configure environment variables
# 3. Deploy with automatic HTTPS
```

All these platforms provide **free tiers** and **automatic HTTPS** for webhook security.

## Step 4: Configure Bitbucket Webhook

1. **Go to your repository settings**
   - Navigate to your Bitbucket repository
   - Click "Repository settings" in the left sidebar
   - Click "Webhooks"

2. **Add a new webhook**
   - Click "Add webhook"
   - Title: "AI Code Reviewer"
   - URL: `https://your-domain.com/webhook` (replace with your actual URL)
   - Secret: Use the same value as `WEBHOOK_SECRET` in your `.env` file

3. **Configure triggers**
   Select these triggers:
   - ✅ Pull request created
   - ✅ Pull request updated
   - ❌ Uncheck all others

4. **Save the webhook**
   Click "Save" to create the webhook

## Step 5: Test the Integration

1. **Create a test pull request**
   - Make a small change to your repository
   - Create a pull request

2. **Check for AI comments**
   - The AI reviewer should automatically post comments within 1-2 minutes
   - Check the application logs if no comments appear

3. **Verify the logs**
   ```bash
   # For local deployment
   tail -f logs/ai_reviewer_$(date +%Y%m%d).log
   
   # For Docker deployment
   docker-compose logs -f bitbucket-ai-reviewer
   ```

## Step 6: Troubleshooting

### Common Issues

**Issue: Webhook not triggering**
- Solution: Verify the webhook URL is publicly accessible
- Test: `curl https://your-domain.com/test`

**Issue: Authentication errors**
- Solution: Check your API keys and tokens
- Verify: Bitbucket token has correct permissions

**Issue: Comments not posting**
- Solution: Check Bitbucket API permissions
- Verify: Token includes "Pull requests: Write" permission

**Issue: OpenAI API errors**
- Solution: Verify API key and account credits
- Check: OpenAI account has sufficient balance

### Getting Help

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Test each component** individually:
   - OpenAI API: Check your key works
   - Bitbucket API: Test with a simple curl request
   - Webhook: Verify it's receiving requests

3. **Verify configuration**:
   ```bash
   # Test the service is running
   curl https://your-domain.com/test
   
   # Check webhook endpoint (basic test)
   curl -X POST https://your-domain.com/webhook \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

### Local Development Testing

If you need to test webhooks locally before deploying to production:

**Step 1: Start Your Flask Application**
```bash
# Make sure you have configured .env file first
python app.py
# Flask server starts on http://localhost:5000
```

**Step 2: Expose Locally (Choose One Option)**

**Option 1: ngrok (Recommended)**
```bash
# Download ngrok from https://ngrok.com
# Extract and run:
./ngrok http 5000
# Copy the https://xxxx.ngrok.io URL for your Bitbucket webhook
```

**Option 2: SSH Tunnel**
```bash
# If you have access to a server with SSH:
ssh -R 80:localhost:5000 serveo.net
# Use the provided URL for webhook
```

**Option 3: Cloud Development**
- **GitHub Codespaces**: Flask port 5000 automatically exposed
- **Replit**: Public URL provided automatically
- **Gitpod**: Port forwarding built-in

**Step 3: Test Your Setup**
```bash
# Test your public URL:
curl https://your-tunnel-url.com/test

# Should return: {"status": "success", "message": "Server is accessible"}
```

**Note:** Local tunnels are temporary and only for development. Use cloud deployment for production.

## Advanced Configuration

### Custom Review Prompts

To customize the AI review behavior, modify the prompt in `src/utils/openai_client.py`.

### Rate Limiting

Adjust the `API_RATE_LIMIT` environment variable to control how many requests per hour are allowed per IP address.

### Logging

Configure logging level with the `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed logging
- `INFO`: Normal logging (default)
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors

## Security Best Practices

1. **Always use HTTPS** for webhook URLs in production
2. **Set a strong webhook secret** to verify request authenticity
3. **Regularly rotate API keys** and access tokens
4. **Monitor logs** for suspicious activity
5. **Keep dependencies updated** for security patches

## Next Steps

Once setup is complete:
- Monitor the AI reviewer's performance on a few pull requests
- Adjust the review criteria if needed
- Consider setting up alerts for application errors
- Train your team on interpreting AI feedback

---

**Congratulations!** Your Bitbucket AI Code Reviewer is now set up and ready to help improve code quality across your team.