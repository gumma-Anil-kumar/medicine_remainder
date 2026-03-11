import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Create a minimal Flask app
app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')  # Set default sender
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Print configuration (without password)
print("📧 Email Configuration:")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'Not set'}")

# Initialize mail
mail = Mail(app)

def test_email_detailed():
    """Test sending an email with detailed error handling"""
    try:
        with app.app_context():
            # Create message with explicit sender
            msg = Message(
                subject="🧪 Test Email from Medicine Reminder",
                sender=app.config['MAIL_USERNAME'],  # Explicit sender
                recipients=[app.config['MAIL_USERNAME']],  # Send to yourself
                body="""Hello!

This is a test email from your Medicine Reminder application.

If you're receiving this, your email configuration is working correctly!

Time sent: {0}

Best regards,
Medicine Reminder App
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            
            # Also add HTML version
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ padding: 20px; }}
                    .success {{ color: green; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 class="success">✅ Email Test Successful!</h2>
                    <p>Hello!</p>
                    <p>This is a test email from your Medicine Reminder application.</p>
                    <p>If you're receiving this, your email configuration is working correctly!</p>
                    <p><strong>Time sent:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr>
                    <p>Best regards,<br>Medicine Reminder App</p>
                </div>
            </body>
            </html>
            """
            
            print("\n📤 Attempting to send email...")
            mail.send(msg)
            print("✅ Email sent successfully!")
            print(f"📨 Check your inbox at: {app.config['MAIL_USERNAME']}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print("\n🔍 Troubleshooting tips:")
        
        if "Authentication failed" in str(e):
            print("  • Check if your email password is correct")
            print("  • For Gmail, use an App Password instead of regular password")
            print("  • Enable 2-Factor Authentication and generate App Password")
        elif "smtplib.SMTPException" in str(e):
            print("  • Check if MAIL_SERVER and MAIL_PORT are correct")
            print("  • Verify TLS/SSL settings")
        elif "Connection refused" in str(e):
            print("  • Check your internet connection")
            print("  • Verify if your firewall is blocking the connection")
        else:
            print(f"  • Error type: {type(e).__name__}")
        
        return False

def test_email_with_different_providers():
    """Test email with different providers"""
    
    # Test Gmail configuration
    print("\n📧 Testing Gmail Configuration...")
    gmail_configs = [
        {
            'name': 'Gmail (TLS)',
            'server': 'smtp.gmail.com',
            'port': 587,
            'tls': True,
            'ssl': False
        },
        {
            'name': 'Gmail (SSL)',
            'server': 'smtp.gmail.com',
            'port': 465,
            'tls': False,
            'ssl': True
        }
    ]
    
    for config in gmail_configs:
        print(f"\nTesting: {config['name']}")
        app.config['MAIL_SERVER'] = config['server']
        app.config['MAIL_PORT'] = config['port']
        app.config['MAIL_USE_TLS'] = config['tls']
        app.config['MAIL_USE_SSL'] = config['ssl']
        
        try:
            with app.app_context():
                msg = Message(
                    subject=f"Test Email - {config['name']}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[app.config['MAIL_USERNAME']],
                    body="This is a test email."
                )
                mail.send(msg)
                print(f"✅ Success with {config['name']}")
        except Exception as e:
            print(f"❌ Failed with {config['name']}: {e}")

if __name__ == "__main__":
    from datetime import datetime
    
    print("=" * 50)
    print("📧 EMAIL CONFIGURATION TEST")
    print("=" * 50)
    
    # Check if email credentials are set
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("❌ Email credentials not found in .env file!")
        print("\nPlease add to your .env file:")
        print("MAIL_USERNAME=your-email@gmail.com")
        print("MAIL_PASSWORD=your-app-password")
    else:
        # Run the test
        test_email_detailed()
        
        # Optional: Test with different configurations
        # test_email_with_different_providers()
    
    print("\n" + "=" * 50)