# 🤖 Bitbucket AI Code Reviewer

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-orange.svg)](https://openai.com)

> **Transform your code reviews with AI-powered intelligence**

An intelligent, automated code review bot that revolutionizes your development workflow by providing instant, comprehensive analysis of every pull request. Powered by OpenAI's advanced language models, it delivers expert-level feedback on code quality, security vulnerabilities, performance optimizations, and documentation improvements - **completely free and open source**.

## 🌟 Why Choose Bitbucket AI Code Reviewer?

**🚀 Instant Expert Reviews**
- Get comprehensive code analysis in seconds, not hours
- Catch bugs, security issues, and performance problems before they reach production
- Maintain consistent code quality across your entire team

**🔒 Security-First Approach**
- Identifies potential security vulnerabilities automatically
- Validates input sanitization and authentication patterns
- Flags insecure configurations and credential exposure risks

**⚡ Performance Optimization**
- Spots inefficient algorithms and data structures
- Suggests optimizations for better runtime performance
- Identifies memory leaks and resource management issues

**📚 Documentation Excellence**
- Recommends missing documentation for complex functions
- Suggests clearer variable and function naming
- Improves code readability and maintainability

**🔧 Zero Configuration Required**
- Works out-of-the-box with any Bitbucket repository
- Simple webhook integration - setup in under 5 minutes
- Docker deployment for maximum portability

## ✨ Core Features

| Feature | Description | Impact |
|---------|-------------|---------|
| 🤖 **AI-Powered Analysis** | Advanced GPT-based code review with context understanding | Catches issues human reviewers might miss |
| 💬 **Inline Comments** | Precise feedback posted directly on problematic code lines | Streamlines developer workflow |
| 🔄 **Real-time Integration** | Automatic analysis triggered by pull request events | Zero manual intervention required |
| 🛡️ **Security Scanning** | Identifies vulnerabilities, injection risks, and auth issues | Prevents security breaches before deployment |
| ⚡ **Performance Insights** | Spots algorithmic inefficiencies and optimization opportunities | Improves application speed and resource usage |
| 📋 **Quality Metrics** | Enforces coding standards and best practices | Maintains consistent codebase quality |
| 🔒 **Enterprise Security** | Webhook signature verification and rate limiting | Production-ready security features |
| 🐳 **Docker Ready** | One-command deployment with Docker Compose | Deploy anywhere in minutes |

## 🚀 Quick Start (5 Minutes Setup)

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/bitbucket-ai-reviewer.git
cd bitbucket-ai-reviewer

# 2. Configure your environment
cp .env.example .env
# Edit .env with your API keys (see configuration section below)

# 3. Deploy with Docker
docker-compose up -d

# 4. Verify it's running
curl http://localhost:5000/test
```

### Option 2: Local Python Installation

```bash
# 1. Clone and setup
git clone https://github.com/your-username/bitbucket-ai-reviewer.git
cd bitbucket-ai-reviewer
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Add your OpenAI API key and Bitbucket credentials

# 3. Run the application
python app.py

# 4. Test the installation
python test_installation.py
```

### 🎯 What You Need

| Requirement | Where to Get It | Time Needed |
|-------------|-----------------|-------------|
| 🔑 **OpenAI API Key** | [OpenAI Platform](https://platform.openai.com/api-keys) | 2 minutes |
| 🔐 **Bitbucket Token** | [Bitbucket Settings](https://bitbucket.org/account/settings/) | 2 minutes |
| 🌐 **Public Deployment** | [Heroku](https://heroku.com), [Railway](https://railway.app), or [Render](https://render.com) (all free) | 5 minutes |

## 🌐 Deployment Options

### 🚀 **Cloud Deployment (Production Ready)**

**Heroku (Easiest)**
```bash
# Install Heroku CLI, then:
heroku create your-ai-reviewer
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set BITBUCKET_ACCESS_TOKEN=your_token_here
heroku config:set WEBHOOK_SECRET=your_secret_here
git push heroku main
```

**Railway (Modern)**
```bash
# Install Railway CLI, then:
railway login
railway new
railway add
railway deploy
# Configure environment variables in Railway dashboard
```

**Render (Simple)**
```bash
# 1. Connect your GitHub repo to Render
# 2. Set environment variables in Render dashboard
# 3. Deploy automatically on git push
```

### 🐳 **Docker Deployment**

**Docker Compose (Recommended)**
```bash
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```

**Docker CLI**
```bash
docker build -t ai-code-reviewer .
docker run -d -p 5000:5000 --env-file .env ai-code-reviewer
```

### 🔧 **Local Development Only**

For local testing (not production):
```bash
# Option 1: LocalTunnel (free alternative to ngrok)
npx localtunnel --port 5000

# Option 2: Cloudflare Tunnel (free)
cloudflared tunnel --url http://localhost:5000
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `BITBUCKET_ACCESS_TOKEN` | Yes* | Bitbucket access token (preferred) |
| `BITBUCKET_APP_PASSWORD` | Yes* | Bitbucket app password (alternative) |
| `WEBHOOK_SECRET` | Recommended | Secret for webhook signature verification |
| `PORT` | No | Server port (default: 5000) |
| `FLASK_DEBUG` | No | Enable debug mode (default: false) |
| `API_RATE_LIMIT` | No | Requests per hour limit (default: 60) |

*Choose either `BITBUCKET_ACCESS_TOKEN` or `BITBUCKET_APP_PASSWORD`

### Getting API Credentials

#### OpenAI API Key
1. Visit [OpenAI API Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key to your `.env` file

#### Bitbucket Access Token (Recommended)
1. Go to Bitbucket Settings → App passwords
2. Create a new app password with these permissions:
   - Repositories: Read
   - Pull requests: Read, Write
3. Copy the token to your `.env` file

#### Bitbucket App Password (Alternative)
1. Go to Bitbucket Settings → Personal Bitbucket settings → App passwords
2. Create a new app password with pull request permissions
3. Copy the password to your `.env` file

### Webhook Setup

1. **Configure the webhook in your Bitbucket repository:**
   - Go to Repository Settings → Webhooks
   - Add webhook URL: `https://your-domain.com/webhook`
   - Select triggers: "Pull request created" and "Pull request updated"
   - Add the webhook secret (recommended for security)

2. **Test the webhook:**
   ```bash
   curl -X GET https://your-domain.com/test
   ```

## How It Works

1. **Webhook Reception**: Bitbucket sends a webhook when PR events occur
2. **Event Filtering**: The system processes only pull request events
3. **Diff Retrieval**: Fetches the complete diff from the Bitbucket API
4. **AI Analysis**: Sends the diff to OpenAI for comprehensive code review
5. **Comment Posting**: Posts structured feedback as comments on the PR

### Review Categories

The AI reviewer analyzes code across these categories:

- **Code Quality**: Best practices, maintainability, code patterns
- **Bugs & Logic**: Runtime errors, edge cases, error handling
- **Security**: Vulnerabilities, injection risks, credential exposure
- **Performance**: Optimization opportunities, algorithmic efficiency
- **Documentation**: Missing documentation, unclear code

## API Endpoints

- `GET /` - Health check endpoint
- `GET /test` - Detailed server status
- `POST /webhook` - Bitbucket webhook endpoint

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Local Development
```bash
export FLASK_DEBUG=true
python app.py
```

### Project Structure
```
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI entry point
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── .env.example         # Environment template
└── src/
    └── utils/
        ├── bitbucket_client.py    # Bitbucket API integration
        ├── openai_client.py       # OpenAI API integration
        └── webhook_utils.py       # Webhook processing
```

## Security Considerations

- **Webhook Signatures**: Always configure `WEBHOOK_SECRET` for production
- **API Keys**: Store all API keys securely and never commit them to version control
- **Rate Limiting**: Built-in rate limiting protects against abuse
- **Input Validation**: All webhook payloads are validated before processing

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify your API key is correct and has sufficient credits
   - Check the logs for detailed error messages

2. **Bitbucket Authentication Errors**
   - Ensure your access token/app password has the correct permissions
   - Verify the token hasn't expired

3. **Webhook Not Triggering**
   - Check the webhook URL is accessible from the internet
   - Verify the webhook triggers are set to PR events
   - Test with `/test` endpoint first

4. **Comments Not Posting**
   - Check Bitbucket API permissions
   - Verify the repository name format in logs
   - Ensure the webhook payload contains valid PR information

### Logs

Application logs are stored in the `logs/` directory with daily rotation. Check these files for debugging:

```bash
tail -f logs/ai_reviewer_$(date +%Y%m%d).log
```

## 🤝 Contributing

We welcome contributions! This project thrives on community input and improvements.

### How to Contribute

1. **🍴 Fork the repository**
2. **🌿 Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **✨ Make your changes** with proper testing
4. **📝 Add tests** for new functionality
5. **🚀 Submit a pull request** with a clear description

### Development Setup

```bash
git clone https://github.com/your-username/bitbucket-ai-reviewer.git
cd bitbucket-ai-reviewer
pip install -r requirements.txt
cp .env.example .env
# Configure your development environment
python test_installation.py
```

### Areas We Need Help With

- 🌐 **Additional Git Platforms**: GitLab, GitHub integration
- 🔧 **New AI Models**: Claude, Gemini support
- 📊 **Analytics Dashboard**: Code quality metrics visualization
- 🧪 **Testing**: Expand test coverage
- 📚 **Documentation**: Tutorials and examples

## ⭐ Show Your Support

If this project helps you, please consider:
- ⭐ **Starring the repository**
- 🐛 **Reporting bugs** and suggesting features
- 💬 **Sharing with your team** and on social media
- 🤝 **Contributing code** or documentation

## 📄 License

**MIT License** - Use it anywhere, modify freely, no strings attached!

See the [LICENSE](LICENSE) file for full details.

**Created with ❤️ by [Behzad Torkian](https://github.com/your-username)**

## 🆘 Support & Community

### Getting Help

- 📖 **Documentation**: Start with [SETUP.md](SETUP.md) for detailed instructions
- 🐛 **Issues**: [Open an issue](https://github.com/your-username/bitbucket-ai-reviewer/issues) for bugs or feature requests
- 💬 **Discussions**: Share ideas and ask questions in [Discussions](https://github.com/your-username/bitbucket-ai-reviewer/discussions)

### Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| 🚫 Webhook not triggering | Check URL accessibility with `curl https://your-domain.com/test` |
| 🔑 OpenAI API errors | Verify API key and account credits |
| 🔐 Bitbucket auth issues | Ensure token has "Pull requests: Write" permission |
| 💬 Comments not posting | Check logs for detailed error messages |

---

<div align="center">

**🚀 Ready to revolutionize your code reviews?**

[⭐ Star this repo](https://github.com/your-username/bitbucket-ai-reviewer) | [🍴 Fork it](https://github.com/your-username/bitbucket-ai-reviewer/fork) | [📖 Read the docs](SETUP.md)

*Built for developers, by developers. Made with 🤖 AI and ❤️ open source.*

</div>