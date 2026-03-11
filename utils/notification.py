from flask_mail import Mail, Message
from config import Config
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.mail = None
        self.mail_initialized = False
        self.app = None
        
    def init_mail(self, app):
        """Initialize mail with Flask app"""
        try:
            self.mail = Mail(app)
            self.app = app
            self.mail_initialized = True
            logger.info("✅ Mail client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize mail: {e}")
    
    def generate_taken_url(self, history_id):
        """Generate URL for marking medicine as taken"""
        try:
            base_url = f"{Config.PREFERRED_URL_SCHEME}://{Config.SERVER_NAME}"
            taken_url = f"{base_url}/mark-taken/{history_id}"
            return taken_url
        except Exception as e:
            logger.error(f"Error generating URL: {e}")
            return f"http://127.0.0.1:5000/mark-taken/{history_id}"
    
    def send_email_reminder(self, to_email, medicine_name, time, history_id):
        """Send email reminder with clickable button"""
        if not self.mail_initialized or not self.mail:
            logger.error("❌ Mail client not initialized")
            return False
        
        if not to_email:
            logger.error("❌ No email address provided")
            return False
        
        try:
            taken_url = self.generate_taken_url(history_id)
            
            msg = Message(
                subject="💊 Medicine Reminder - Time to take your medicine",
                sender=Config.MAIL_USERNAME,
                recipients=[to_email]
            )
            
            # Plain text version
            msg.body = f"""
Hello,

This is a reminder to take your medicine: {medicine_name} at {time}.

To confirm you've taken it, click this link:
{taken_url}

Stay healthy! 🌟
            """
            
            # HTML version with button
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .medicine-name {{ color: #007bff; font-size: 24px; font-weight: bold; }}
                    .time {{ color: #28a745; font-size: 20px; }}
                    .button {{ 
                        background-color: #28a745; 
                        color: white; 
                        padding: 10px 20px; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        display: inline-block;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>💊 Medicine Reminder</h2>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>Time to take your medicine:</p>
                        <p class="medicine-name">{medicine_name}</p>
                        <p>Scheduled time: <span class="time">{time}</span></p>
                        <p>
                            <a href="{taken_url}" class="button">✓ I'VE TAKEN IT</a>
                        </p>
                        <p>Stay healthy! 🌟</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.mail.send(msg)
            logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}")
            return False
    
    """def send_sms_reminder(self, to_phone, medicine_name, time, history_id):
    
        if not self.twilio_client:
            logger.warning("❌ Twilio client not initialized")
            return False
        
        if not to_phone:
            logger.error("❌ No phone number provided")
            return False
        
        try:
            # Generate the taken URL (same as email)
            taken_url = self.generate_taken_url(history_id)
            
            # Create message with emojis and link
            message_body = f"💊 Medicine Reminder: Time to take {medicine_name} at {time}. After taking, click to confirm: {taken_url}"
            
            # SMS has length limits, so keep it concise
            if len(message_body) > 160:
                # Shorten if needed
                message_body = f"Take {medicine_name} at {time}. Confirm: {taken_url}"
            
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(f"✅ SMS sent successfully to {to_phone}")
            logger.info(f"   Message SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ SMS sending failed: {e}")
            
            # Handle specific Twilio errors
            error_str = str(e)
            if "20003" in error_str:
                logger.error("   Authentication failed - check your Account SID and Auth Token")
            elif "21211" in error_str:
                logger.error("   Invalid phone number format - use E.164 format: +[country][number]")
            elif "21408" in error_str:
                logger.error("   Permission error - trial accounts can only send to verified numbers")
            elif "30007" in error_str or "30034" in error_str:
                logger.error("   For US numbers: You need A2P 10DLC registration [citation:6]")
            
            return False"""
        
    """def make_phone_call(self, to_phone, medicine_name):
        
        if not self.twilio_client:
            logger.warning("Twilio client not initialized")
            return False
        
        try:
            # You need to host this TwiML somewhere
            twiml_url = "http://your-domain.com/twilio/voice.xml"
            
            call = self.twilio_client.calls.create(
                url=twiml_url,
                to=to_phone,
                from_=Config.TWILIO_PHONE_NUMBER
            )
            logger.info(f"Call initiated to {to_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Call failed: {e}")
            return False"""