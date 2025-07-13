# Seek Bot - Automated Job Application System

An intelligent, anti-detection job scraping and auto-application bot for Seek.com.au. Built with aggressive efficiency and bulletproof error handling.

## ⚠️ Legal Disclaimer

**READ THIS BEFORE USING:**
- This tool is for educational and personal use only
- You are responsible for compliance with Seek.com.au's Terms of Service
- The authors are not liable for any account suspensions, bans, or legal issues
- Use at your own risk - automated job applications may violate platform policies
- Always review applications before submission in production environments

## 🚀 Features

### Core Functionality
- **Stealth Mode**: Advanced anti-detection with browser fingerprinting, human-like behavior simulation
- **Smart Matching**: Intelligent job filtering based on keywords, salary, location, experience
- **Auto-Application**: Automated job applications with custom cover letters and CV uploads
- **Real-time Dashboard**: Web-based control panel with live status monitoring
- **JSON Storage**: Lightweight file-based storage for jobs, applications, and logs
- **Error Recovery**: Comprehensive error handling with retry mechanisms

### Anti-Detection Features
- Human-like mouse movements and typing patterns
- Random delays and behavioral simulation
- Browser fingerprint masking
- User agent rotation
- Session persistence
- Request rate limiting

### Web Interface
- Start/Stop bot controls
- Real-time status monitoring
- Job queue visualization
- Application history tracking
- Settings management
- Structured log viewer

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- Chrome browser (latest version)
- Linux/macOS (Pop!_OS recommended)

### Setup

1. **Clone and setup:**
```bash
git clone <repository-url>
cd seek-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Create directory structure:**
```bash
mkdir -p data
chmod +x main.py
```

3. **Initialize configuration:**
```bash
# Copy example config
cp config/settings.example.json config/settings.json
# Edit with your credentials
nano config/settings.json
```

4. **Set up Chrome driver:**
```bash
# The bot uses undetected-chromedriver which handles this automatically
# Ensure Chrome is installed and up to date
```

## 📁 Project Structure

```
seek-bot/
├── config/
│   ├── __init__.py
│   └── settings.json          # User configuration
├── core/
│   ├── __init__.py
│   ├── auth.py               # Seek authentication
│   ├── scraper.py            # Job scraping engine
│   ├── applicator.py         # Auto-application logic
│   └── anti_detection.py     # Stealth mechanisms
├── utils/
│   ├── __init__.py
│   ├── browser.py            # Browser management
│   ├── storage.py            # JSON file operations
│   ├── logging.py            # Structured logging
│   └── errors.py             # Error handling
├── api/
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   └── routes.py             # API endpoints
├── web/
│   ├── static/
│   │   ├── style.css         # Dashboard styles
│   │   └── app.js            # Frontend logic
│   └── templates/
│       └── index.html        # Dashboard UI
├── data/
│   ├── jobs.json            # Scraped job data
│   ├── applied.json         # Application history
│   └── logs.json            # Application logs
├── main.py                  # CLI entry point
└── requirements.txt         # Dependencies
```

## ⚙️ Configuration

### Settings File (`config/settings.json`)

```json
{
  "user": {
    "email": "your.email@example.com",
    "password": "your_secure_password",
    "agreement_accepted": true,
    "agreement_timestamp": "2025-01-15T10:30:00Z"
  },
  "job_preferences": {
    "keywords": ["python", "backend", "software engineer", "developer"],
    "locations": ["Sydney", "Melbourne", "Brisbane", "Remote"],
    "salary_min": 80000,
    "salary_max": 150000,
    "job_types": ["full-time", "contract", "part-time"],
    "experience_levels": ["entry", "mid", "senior"],
    "exclude_companies": ["Company A", "Company B"]
  },
  "application_settings": {
    "auto_apply": true,
    "max_applications_per_day": 20,
    "max_applications_per_session": 10,
    "cover_letter_template": "Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position at {company_name}...",
    "cv_path": "/path/to/your/cv.pdf"
  },
  "anti_detection": {
    "min_delay": 2,
    "max_delay": 8,
    "use_proxy": false,
    "proxy_list": [],
    "user_agent_rotation": true,
    "headless": false
  },
  "deepseek_api": {
    "api_key": "your_deepseek_api_key",
    "enabled": false,
    "model": "deepseek-chat"
  }
}
```

### Required Fields
- `user.email`: Your Seek.com.au email
- `user.password`: Your Seek.com.au password
- `user.agreement_accepted`: Must be `true` to run
- `job_preferences.keywords`: Job search terms
- `application_settings.cv_path`: Path to your CV file

## 🚀 Usage

### CLI Mode
```bash
# Run bot once
python main.py

# With verbose logging
python main.py --verbose

# Dry run (scrape only, no applications)
python main.py --dry-run
```

### Web Dashboard
```bash
# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access dashboard
open http://localhost:8000
```

### Dashboard Features
- **Start Bot**: Begin job scraping and application process
- **Stop Bot**: Gracefully halt operations
- **Status Monitor**: Real-time progress tracking
- **Job Queue**: View scraped jobs and application status
- **Settings**: Update configuration via web form
- **Logs**: View structured application logs

## 🔧 Advanced Configuration

### Anti-Detection Tuning
```json
{
  "anti_detection": {
    "min_delay": 3,           # Minimum delay between actions
    "max_delay": 12,          # Maximum delay between actions
    "typing_speed": 0.1,      # Seconds between keystrokes
    "mouse_speed": 0.05,      # Mouse movement speed
    "scroll_behavior": true,  # Simulate scrolling
    "tab_switching": true     # Simulate tab management
  }
}
```

### Application Limits
```json
{
  "application_settings": {
    "max_applications_per_day": 50,
    "max_applications_per_session": 25,
    "cooldown_between_applications": 180,  # seconds
    "skip_already_applied": true,
    "application_timeout": 300             # seconds
  }
}
```

## 📊 Data Storage

### Jobs Data (`data/jobs.json`)
```json
{
  "jobs": [
    {
      "id": "job_123456",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "Sydney",
      "salary": "120000-150000",
      "url": "https://seek.com.au/job/123456",
      "scraped_at": "2025-01-15T10:30:00Z",
      "match_score": 0.85,
      "applied": false
    }
  ]
}
```

### Application History (`data/applied.json`)
```json
{
  "applications": [
    {
      "job_id": "job_123456",
      "applied_at": "2025-01-15T11:00:00Z",
      "status": "success",
      "response_time": 15.3,
      "error": null
    }
  ]
}
```

## 🛡️ Error Handling

### Error Types
- **AuthError**: Authentication failures
- **ScrapingError**: Web scraping issues
- **ApplicationError**: Job application failures
- **NetworkError**: Connection problems
- **RateLimitError**: Rate limiting detection

### Recovery Mechanisms
- Automatic retry with exponential backoff
- Session refresh on auth failures
- Graceful degradation on rate limits
- Comprehensive error logging

## 🔍 Monitoring & Logging

### Log Levels
- **DEBUG**: Detailed operation info
- **INFO**: General operation status
- **WARNING**: Potential issues
- **ERROR**: Operation failures
- **CRITICAL**: System failures

### Log Format
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "module": "core.scraper",
  "message": "Scraped 25 jobs successfully",
  "context": {
    "job_count": 25,
    "search_terms": ["python", "backend"],
    "execution_time": 12.5
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**Authentication Failures:**
```bash
# Check credentials
cat config/settings.json | jq '.user'

# Test login manually
python -c "from core.auth import SeekAuth; import asyncio; asyncio.run(SeekAuth().login())"
```

**Browser Issues:**
```bash
# Update Chrome
sudo apt update && sudo apt upgrade google-chrome-stable

# Clear browser cache
rm -rf ~/.cache/google-chrome/
```

**Rate Limiting:**
```bash
# Increase delays in config
jq '.anti_detection.min_delay = 5 | .anti_detection.max_delay = 15' config/settings.json
```

**Application Failures:**
```bash
# Check CV path
ls -la "$(jq -r '.application_settings.cv_path' config/settings.json)"

# Validate cover letter template
python -c "print(open('config/settings.json').read())" | jq '.application_settings.cover_letter_template'
```

## 🔒 Security Best Practices

1. **Credentials**: Never commit credentials to version control
2. **Encryption**: Store passwords encrypted (implementation pending)
3. **Rate Limiting**: Respect platform limits to avoid detection
4. **VPN/Proxy**: Consider using residential proxies for large-scale operations
5. **Session Management**: Implement proper session cleanup

## 🚀 Future Enhancements

### Planned Features
- **DeepSeek Integration**: AI-powered cover letter generation
- **Multi-platform Support**: Indeed, LinkedIn integration
- **Advanced Analytics**: Success rate tracking, A/B testing
- **Notification System**: Email/Slack alerts for applications
- **Docker Support**: Containerized deployment
- **Database Migration**: PostgreSQL/MongoDB support

### DeepSeek AI Integration
```python
# Future implementation for AI-powered applications
async def generate_cover_letter(job_data: dict) -> str:
    """Generate personalized cover letter using DeepSeek AI"""
    # Implementation pending
    pass
```

## 📈 Performance Optimization

### Scaling Considerations
- **Concurrent Sessions**: Multiple browser instances
- **Queue Management**: Job application queuing
- **Resource Monitoring**: CPU/Memory usage tracking
- **Database Optimization**: Indexing for large datasets

### Benchmarks
- **Scraping Speed**: ~100 jobs/minute
- **Application Rate**: ~5 applications/minute
- **Memory Usage**: ~200MB average
- **CPU Usage**: ~15% average

## 🤝 Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .
isort .

# Type checking
mypy .
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints extensively
- Comprehensive error handling
- Structured logging throughout
- Unit tests for all modules

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `data/logs.json`
3. Open an issue with detailed error information
4. Include system information and configuration (sanitized)

## 🎯 Disclaimer

This tool is designed for educational purposes and personal job searching. Users are responsible for:
- Complying with platform terms of service
- Ensuring ethical usage
- Maintaining account security
- Following local laws and regulations

**Use responsibly and at your own risk.**