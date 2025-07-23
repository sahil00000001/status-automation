# Yondrone Status Monitor

Automated monitoring system that captures screenshots of the Yondrone status page and sends email reports every 2 hours.

## Features

- Captures full-page screenshots of https://status.yondrone.com/
- Sends professional HTML emails with screenshots attached
- Runs automatically every 2 hours
- Includes IST and UK timezone information
- Anti-spam measures implemented

## Deployment on Render

This project is configured for easy deployment on Render as a background worker.

### Prerequisites

- Render account (https://render.com)
- GitHub account
- Git installed locally

### Quick Deploy

1. Push this code to your GitHub repository
2. Connect your GitHub account to Render
3. Create a new Background Worker service
4. Select your repository
5. Render will automatically detect the configuration and deploy

### Manual Configuration

If you prefer manual setup:
- **Service Type**: Background Worker
- **Runtime**: Docker
- **Docker Path**: ./Dockerfile
- **Environment Variables**: None required (all config is in the code)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run locally
python monitor.py
```

## Email Configuration

Current configuration sends emails:
- **From**: vashishtsahil99@gmail.com
- **To**: sahil.vashisht@podtech.com
- **CC**: dikshant.singh@podtech.com

## Monitoring

- Check Render dashboard for service status
- View logs in real-time from Render dashboard
- Service automatically restarts if it crashes

## Support

For issues or questions, contact the technical team.