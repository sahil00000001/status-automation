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
    """Create professional HTML email body with larger text and inline screenshot"""
    ist_time, uk_time = get_formatted_times()
    
    html_body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.8;
                    color: #2c3e50;
                    font-size: 16px;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 30px;
                    background-color: #ffffff;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                    color: white;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 18px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 20px;
                    font-size: 16px;
                }}
                .content p {{
                    margin: 15px 0;
                    font-size: 16px;
                    line-height: 1.8;
                }}
                .details-box {{
                    background-color: #f8f9fa;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 25px 0;
                }}
                .details-box h3 {{
                    margin: 0 0 15px 0;
                    color: #495057;
                    font-size: 20px;
                }}
                .details-box ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .details-box li {{
                    margin: 10px 0;
                    font-size: 16px;
                    color: #495057;
                }}
                .timestamp {{
                    color: #667eea;
                    font-weight: bold;
                    font-size: 18px;
                }}
                .status-badge {{
                    display: inline-block;
                    background-color: #28a745;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .screenshot-section {{
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 30px;
                    margin: 30px 0;
                    text-align: center;
                }}
                .screenshot-title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: #495057;
                    margin-bottom: 20px;
                }}
                .screenshot-container {{
                    border: 3px solid #dee2e6;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    background-color: white;
                    padding: 10px;
                }}
                .screenshot-img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                }}
                .notice {{
                    background-color: #e3f2fd;
                    border-left: 5px solid #2196F3;
                    padding: 15px 20px;
                    margin: 25px 0;
                    border-radius: 5px;
                }}
                .notice p {{
                    margin: 0;
                    font-size: 15px;
                    color: #1565C0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 30px;
                    border-top: 2px solid #e0e0e0;
                    text-align: center;
                    color: #666;
                }}
                .footer p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background-color: #5a67d8;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Yondrone Status Monitor</h1>
                    <p>Automated Status Report</p>
                </div>
                
                <div class="content">
                    <p style="font-size: 18px;"><strong>Dear Team,</strong></p>
                    
                    <p>The automated monitoring system has successfully captured the current status of the Yondrone platform.</p>
                    
                    <div class="details-box">
                        <h3>📊 Capture Details</h3>
                        <ul>
                            <li><strong>URL Monitored:</strong> <a href="{TARGET_URL}" style="color: #667eea; font-size: 16px;">{TARGET_URL}</a></li>
                            <li><strong>Timestamp:</strong> <span class="timestamp">{ist_time} ({uk_time})</span></li>
                            <li><strong>Status:</strong> <span class="status-badge">✓ Successfully Captured</span></li>
                        </ul>
                    </div>
                    
                    <div class="screenshot-section">
                        <div class="screenshot-title">📸 Current Status Screenshot</div>
                        <div class="screenshot-container">
                            <img src="cid:screenshot" alt="Yondrone Status Screenshot" class="screenshot-img" />
                        </div>
                        <p style="margin-top: 15px; color: #666; font-size: 14px;">
                            <em>Screenshot captured at {ist_time}</em>
                        </p>
                    </div>
                    
                    <div class="notice">
                        <p><strong>🔔 Important:</strong> This is an authorized automated monitoring email.</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{TARGET_URL}" class="button">Visit Yondrone Status Page</a>
                    </p>
                    
                    <p>This automated report is generated every 2 hours to ensure continuous monitoring of the Yondrone platform's availability and status.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Yondrone Status Monitoring System v1.0</strong></p>
                    <p>This is an automated message generated every 2 hours.</p>
                    <p style="font-size: 12px; color: #999;">For any queries or issues, please contact the technical team.</p>
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
        msg = MIMEMultipart('related')  # Changed back to 'related' for inline images
        
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
        
        # Create alternative part for plain text and HTML
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
        
        # Attach screenshot with Content-ID for inline display
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                img = MIMEImage(f.read())
                # Important: Set Content-ID for inline display
                img.add_header('Content-ID', '<screenshot>')
                img.add_header('Content-Disposition', 'inline', 
                             filename=f'yondrone_status_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
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