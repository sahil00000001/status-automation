import os
import time
import logging
from datetime import datetime
import pytz
import requests
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import schedule
import tempfile
import email.utils  # Added for better email headers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "vashishtsahil99@gmail.com"
APP_PASSWORD = "zzzuvtothvigzktq"
TO_EMAIL = "sahil.vashisht@podtech.com"
CC_EMAIL = "dikshant.singh@podtech.com"

# Target URL
TARGET_URL = "https://status.yondrone.com/"

def take_screenshot_playwright(url):
    """Take screenshot using Playwright - much simpler and reliable"""
    screenshot_path = None
    
    try:
        with sync_playwright() as p:
            # Launch browser
            logger.info("Launching browser...")
            browser = p.chromium.launch(headless=True)
            
            # Create page
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Navigate to URL
            logger.info(f"Loading webpage: {url}")
            page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait a bit for any dynamic content
            page.wait_for_timeout(5000)
            
            # Take full page screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                screenshot_path = tmp_file.name
                page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved successfully")
            
            # Close browser
            browser.close()
            
        return screenshot_path
        
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        raise

def get_formatted_times():
    """Get current time in IST and UK timezones"""
    ist_tz = pytz.timezone('Asia/Kolkata')
    uk_tz = pytz.timezone('Europe/London')
    
    current_time = datetime.now()
    ist_time = current_time.astimezone(ist_tz)
    uk_time = current_time.astimezone(uk_tz)
    
    ist_formatted = ist_time.strftime('%Y-%m-%d %H:%M IST')
    uk_formatted = uk_time.strftime('%H:%M UK')
    
    return ist_formatted, uk_formatted

def create_email_body():
    """Create professional HTML email body"""
    ist_time, uk_time = get_formatted_times()
    
    html_body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .content {{
                    padding: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    font-size: 12px;
                    color: #666;
                }}
                .timestamp {{
                    color: #0066cc;
                    font-weight: bold;
                }}
                .notice {{
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-left: 4px solid #0066cc;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0; color: #2c3e50;">Yondrone Status Monitor</h2>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">Automated Status Report</p>
                </div>
                
                <div class="content">
                    <p>Dear Team,</p>
                    
                    <p>The automated monitoring system has successfully captured the current status of the Yondrone platform.</p>
                    
                    <p><strong>Capture Details:</strong></p>
                    <ul>
                        <li>URL Monitored: <a href="{TARGET_URL}">{TARGET_URL}</a></li>
                        <li>Timestamp: <span class="timestamp">{ist_time} ({uk_time})</span></li>
                        <li>Status: Successfully captured</li>
                    </ul>
                    
                    <div class="notice">
                        <strong>Note:</strong> This is an authorized automated monitoring email from the IT monitoring system. 
                    </div>
                    
                    <p>Please find the full-page screenshot attached to this email for your review.</p>
                    
                    <p>This is an automated report generated every 2 hours to ensure continuous monitoring of the Yondrone status page.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Yondrone Status Monitoring System v1.0</strong><br>
                    This is an automated message. For any queries or issues, please contact the technical team.<br>
                    <small>If this email was incorrectly marked as spam, please mark it as "Not Spam" to ensure future deliveries.</small></p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return html_body

def send_email(screenshot_path):
    """Send email with improved headers to avoid spam filters"""
    try:
        ist_time, uk_time = get_formatted_times()
        
        # More descriptive subject line
        subject = f"[Monitoring Report] Yondrone Platform Status - {ist_time} ({uk_time})"
        
        # Create message with proper headers
        msg = MIMEMultipart('mixed')  # Changed from 'related' to 'mixed'
        
        # Essential headers to avoid spam filters
        msg['From'] = f"Yondrone Monitor <{SENDER_EMAIL}>"
        msg['To'] = TO_EMAIL
        msg['Cc'] = CC_EMAIL
        msg['Subject'] = subject
        msg['Date'] = email.utils.formatdate(localtime=True)
        msg['Message-ID'] = email.utils.make_msgid()
        msg['X-Priority'] = '3'  # Normal priority
        msg['X-Mailer'] = 'Yondrone Status Monitor v1.0'
        msg['Reply-To'] = SENDER_EMAIL
        msg['Importance'] = 'Normal'
        msg['X-MSMail-Priority'] = 'Normal'
        
        # Add both plain text and HTML versions
        msg_alternative = MIMEMultipart('alternative')
        
        # Plain text version (important for spam filters)
        plain_text = f"""
Yondrone Status Monitor - Automated Report

Dear Team,

The automated monitoring system has successfully captured the current status of the Yondrone platform.

Capture Details:
- URL Monitored: {TARGET_URL}
- Timestamp: {ist_time} ({uk_time})
- Status: Successfully captured

IMPORTANT: This is an authorized automated monitoring email from the IT monitoring system. 
Please add this sender to your safe senders list to ensure future reports reach your inbox.

Please find the full-page screenshot attached to this email for your review.

This is an automated report generated every 2 hours to ensure continuous monitoring of the Yondrone status page.

---
Yondrone Status Monitoring System v1.0
This is an automated message. For any queries or issues, please contact the technical team.
If this email was incorrectly marked as spam, please mark it as "Not Spam" to ensure future deliveries.
        """
        
        msg_alternative.attach(MIMEText(plain_text, 'plain'))
        
        # HTML version
        html_body = create_email_body()
        msg_alternative.attach(MIMEText(html_body, 'html'))
        
        # Attach the alternative part
        msg.attach(msg_alternative)
        
        # Attach screenshot with proper headers
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', 
                             filename=f'yondrone_status_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
                img.add_header('Content-ID', '<screenshot>')
                msg.attach(img)
        
        # Send email with explicit encoding
        logger.info("Sending email...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            
            # Send to all recipients
            recipients = [TO_EMAIL, CC_EMAIL]
            server.send_message(msg)
        
        logger.info(f"Email sent successfully!")
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

def monitor_and_report():
    """Main function to take screenshot and send email"""
    logger.info("=" * 50)
    logger.info("Running monitoring task...")
    screenshot_path = None
    
    try:
        # Take screenshot
        screenshot_path = take_screenshot_playwright(TARGET_URL)
        
        # Send email
        send_email(screenshot_path)
        
        logger.info("Task completed successfully!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
    finally:
        # Clean up
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except:
                pass

def main():
    """Main function"""
    logger.info("🚀 Yondrone Status Monitor Starting...")
    logger.info("📧 Email anti-spam measures enabled")
    
    # Run immediately
    monitor_and_report()
    
    # Schedule every 2 hours
    schedule.every(2).hours.do(monitor_and_report)
    
    logger.info("⏰ Scheduled to run every 2 hours")
    logger.info("Press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopped by user")

if __name__ == "__main__":
    main()