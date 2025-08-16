"""
Email Notification System for LinkedIn Scraper
==============================================

Sends email notifications when manual re-login is needed or for daily reports
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import os
from datetime import datetime
import logging

class EmailNotificationSystem:
    """Handle email notifications for LinkedIn scraper events"""
    
    def __init__(self, config_file='email_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load email configuration"""
        default_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': '',
            'recipient_email': '',
            'enabled': False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                self.logger.error(f"Failed to load email config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def send_email(self, subject, body, attachments=None):
        """Send email notification"""
        if not self.config['enabled']:
            self.logger.info(f"Email notifications disabled. Would send: {subject}")
            return False
        
        if not all([self.config['sender_email'], self.config['sender_password'], self.config['recipient_email']]):
            self.logger.error("Email configuration incomplete")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.config['sender_email']
            message["To"] = self.config['recipient_email']
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "html"))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(file_path)}",
                        )
                        message.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls(context=context)
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.sendmail(
                    self.config['sender_email'],
                    self.config['recipient_email'],
                    message.as_string()
                )
            
            self.logger.info(f"✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_cookie_expiry_notification(self):
        """Send notification when LinkedIn cookies have expired"""
        subject = "🔐 LinkedIn Scraper: Manual Login Required"
        
        body = f"""
        <html>
        <body>
            <h2>LinkedIn Scraper Alert</h2>
            <p><strong>Manual re-login required for LinkedIn scraper</strong></p>
            
            <h3>Action Required:</h3>
            <ul>
                <li>Run the cookie extraction script</li>
                <li>Complete manual LinkedIn login with 2FA</li>
                <li>Fresh cookies will be automatically saved</li>
            </ul>
            
            <h3>Quick Fix:</h3>
            <p><code>python cookie_manager.py</code> and choose option 1</p>
            
            <p><em>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            
            <p>This notification was sent automatically by your LinkedIn scraper system.</p>
        </body>
        </html>
        """
        
        return self.send_email(subject, body)
    
    def send_daily_report(self, summary_data, log_file=None):
        """Send daily scraping report"""
        subject = f"📊 LinkedIn Scraper Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Build HTML report
        total_profiles = summary_data.get('total_profiles', 0)
        successful_searches = summary_data.get('successful_searches', 0)
        total_searches = summary_data.get('total_searches', 0)
        
        body = f"""
        <html>
        <body>
            <h2>LinkedIn Scraper Daily Report</h2>
            <p><strong>Date: {summary_data.get('date', 'Unknown')}</strong></p>
            
            <h3>📊 Summary:</h3>
            <ul>
                <li><strong>Total Profiles Found:</strong> {total_profiles}</li>
                <li><strong>Successful Searches:</strong> {successful_searches}/{total_searches}</li>
                <li><strong>Success Rate:</strong> {(successful_searches/total_searches*100) if total_searches > 0 else 0:.1f}%</li>
            </ul>
            
            <h3>🔍 Search Details:</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>Search Name</th>
                    <th>Description</th>
                    <th>Max Profiles</th>
                    <th>Status</th>
                </tr>
        """
        
        for search in summary_data.get('searches', []):
            body += f"""
                <tr>
                    <td>{search.get('name', 'N/A')}</td>
                    <td>{search.get('description', 'N/A')}</td>
                    <td>{search.get('max_profiles', 'N/A')}</td>
                    <td>✅ Configured</td>
                </tr>
            """
        
        body += """
            </table>
            
            <h3>💡 Tips:</h3>
            <ul>
                <li>Results are automatically saved to the scheduled_results/ directory</li>
                <li>Check the logs if any searches failed</li>
                <li>Cookie-based authentication reduces 2FA requirements</li>
            </ul>
            
            <p><em>Generated automatically by LinkedIn Scraper System</em></p>
        </body>
        </html>
        """
        
        attachments = [log_file] if log_file and os.path.exists(log_file) else None
        return self.send_email(subject, body, attachments)
    
    def send_error_notification(self, error_type, error_message, search_name=None):
        """Send notification when scraping errors occur"""
        subject = f"❌ LinkedIn Scraper Error: {error_type}"
        
        body = f"""
        <html>
        <body>
            <h2>LinkedIn Scraper Error Alert</h2>
            
            <h3>Error Details:</h3>
            <ul>
                <li><strong>Type:</strong> {error_type}</li>
                <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                {f'<li><strong>Search:</strong> {search_name}</li>' if search_name else ''}
                <li><strong>Message:</strong> {error_message}</li>
            </ul>
            
            <h3>🔧 Troubleshooting:</h3>
            <ul>
                <li>Check if LinkedIn cookies have expired</li>
                <li>Verify network connectivity</li>
                <li>Check for LinkedIn interface changes</li>
                <li>Review scraper logs for more details</li>
            </ul>
            
            <p><em>This is an automated error notification from your LinkedIn scraper.</em></p>
        </body>
        </html>
        """
        
        return self.send_email(subject, body)

def setup_email_config():
    """Interactive setup for email configuration"""
    print("📧 EMAIL NOTIFICATION SETUP")
    print("=" * 35)
    print("Configure email notifications for LinkedIn scraper events")
    print("-" * 50)
    
    config = {}
    
    print("\\n1. Email Server Configuration:")
    config['smtp_server'] = input("SMTP Server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    
    port_input = input("SMTP Port (default: 587): ").strip()
    config['smtp_port'] = int(port_input) if port_input.isdigit() else 587
    
    print("\\n2. Sender Email Configuration:")
    config['sender_email'] = input("Your email address: ").strip()
    
    print("\\n⚠️ For Gmail, use an App Password instead of your regular password:")
    print("   1. Enable 2FA on your Google account")
    print("   2. Generate an App Password: https://myaccount.google.com/apppasswords")
    print("   3. Use the App Password below")
    
    config['sender_password'] = input("Email password (or App Password): ").strip()
    
    print("\\n3. Notification Settings:")
    config['recipient_email'] = input("Notification recipient email: ").strip() or config['sender_email']
    
    enable_input = input("Enable email notifications? (y/n): ").strip().lower()
    config['enabled'] = enable_input == 'y'
    
    # Save configuration
    with open('email_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\\n✅ Email configuration saved!")
    
    # Test email
    if config['enabled']:
        test_input = input("\\nSend test email? (y/n): ").strip().lower()
        if test_input == 'y':
            notification_system = EmailNotificationSystem()
            success = notification_system.send_email(
                "LinkedIn Scraper Test", 
                "<h2>Test Email</h2><p>Email notifications are working correctly!</p>"
            )
            if success:
                print("✅ Test email sent successfully!")
            else:
                print("❌ Test email failed. Check your configuration.")

if __name__ == "__main__":
    print("📧 Email Notification System")
    print("=" * 30)
    print("1. Setup email configuration")
    print("2. Send test notification")
    print("3. Send cookie expiry notification")
    print("4. View current configuration")
    
    choice = input("\\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        setup_email_config()
    elif choice == "2":
        notification_system = EmailNotificationSystem()
        success = notification_system.send_email(
            "LinkedIn Scraper Test",
            "<h2>Test Notification</h2><p>This is a test email from your LinkedIn scraper system.</p>"
        )
        print("✅ Test sent!" if success else "❌ Test failed!")
    elif choice == "3":
        notification_system = EmailNotificationSystem()
        success = notification_system.send_cookie_expiry_notification()
        print("✅ Notification sent!" if success else "❌ Notification failed!")
    elif choice == "4":
        notification_system = EmailNotificationSystem()
        print(f"\\n📧 Current Configuration:")
        print(f"Enabled: {notification_system.config['enabled']}")
        print(f"SMTP Server: {notification_system.config['smtp_server']}")
        print(f"Sender: {notification_system.config['sender_email']}")
        print(f"Recipient: {notification_system.config['recipient_email']}")
    else:
        print("Invalid choice")
