from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from threading import Lock
from flask import Flask
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReminderScheduler:
    def __init__(self, app, db, notification_service):
        self.app = app  # Store the Flask app
        self.scheduler = BackgroundScheduler(timezone=pytz.UTC)
        self.db = db
        self.notification_service = notification_service
        self.scheduled_jobs = {}
        self.lock = Lock()
        self.is_running = False
        
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Reminder scheduler started")
            
            # Schedule the check_reminders job with proper configuration
            self.scheduler.add_job(
                func=self.check_reminders_wrapper,  # Use wrapper function
                trigger='interval',
                minutes=1,
                id='check_reminders',
                replace_existing=True,
                max_instances=1,
                misfire_grace_time=30
            )
            logger.info("✅ Check reminders job scheduled")
    
    def check_reminders_wrapper(self):
        """Wrapper to run check_reminders within app context"""
        with self.app.app_context():  # Push application context
            self.check_reminders()
    
    def check_reminders(self):
        """Check and send due reminders"""
        with self.lock:
            try:
                logger.info(f"🔍 Checking reminders at {datetime.now()}")
                
                # Get current time in local timezone (Asia/Kolkata for India)
                local_tz = pytz.timezone('Asia/Kolkata')
                current_time = datetime.now(local_tz)
                current_day = current_time.strftime('%a').lower()[:3]
                current_time_str = current_time.strftime('%H:%M')
                
                logger.info(f"Current day: {current_day}, Current time: {current_time_str}")
                
                # Get all medicines
                all_medicines = list(self.db.medicines.find({}))
                logger.info(f"Total medicines in DB: {len(all_medicines)}")
                
                # Check each medicine
                for medicine in all_medicines:
                    try:
                        if 'days' not in medicine:
                            continue
                            
                        if current_day not in medicine['days']:
                            continue
                            
                        timings = medicine['days'][current_day]
                        logger.info(f"Medicine {medicine['medicine_name']} scheduled at: {timings}")
                        
                        for timing in timings:
                            if timing == current_time_str:
                                logger.info(f"⏰ Time to send reminder for {medicine['medicine_name']}")
                                self.send_reminder(medicine, timing)
                                
                    except Exception as e:
                        logger.error(f"Error processing medicine {medicine.get('_id')}: {e}")
                        
            except Exception as e:
                logger.error(f"Error in check_reminders: {e}")
    
    def send_reminder(self, medicine, timing):
        """Send reminder and create history entry"""
        try:
            # Get user information
            user = self.db.get_user_by_id(medicine['user_id'])
            if not user:
                logger.error(f"User not found for medicine {medicine['_id']}")
                return
            
            logger.info(f"Sending reminder to {user.get('email')} for {medicine['medicine_name']}")
            
            # Check if reminder already sent today
            today = datetime.now().strftime('%Y-%m-%d')
            existing_history = self.db.history.find_one({
                'medicine_id': medicine['_id'],
                'date': today,
                'time': timing
            })
            
            if existing_history:
                logger.info(f"Reminder already sent for {medicine['medicine_name']} at {timing}")
                return
            
            # Create history entry
            history_entry = {
                'user_id': medicine['user_id'],
                'medicine_id': medicine['_id'],
                'medicine_name': medicine['medicine_name'],
                'date': today,
                'time': timing,
                'status': 'pending',
                'notification_sent': True,
                'notification_time': datetime.now()
            }
            
            result = self.db.create_history_entry(history_entry)
            history_id = result.inserted_id
            logger.info(f"Created history entry with ID: {history_id}")
            
            # Get user preferences
            preferences = user.get('notification_preferences', {
                'email': True,
                'sms': False,
                'call': False
            })
            
            # Send email reminder with history_id
            if preferences.get('email'):
                try:
                    email_sent = self.notification_service.send_email_reminder(
                        user['email'],
                        medicine['medicine_name'],
                        timing,
                        history_id  # Pass the history_id
                    )
                    if email_sent:
                        logger.info(f"✅ Email sent to {user['email']}")
                    else:
                        logger.error(f"❌ Failed to send email to {user['email']}")
                except Exception as e:
                    logger.error(f"Email sending error: {e}")
            
            # Send SMS if enabled
            """if preferences.get('sms') and user.get('phone'):
                try:
                    sms_sent = self.notification_service.send_sms_reminder(
                        user['phone'],
                        medicine['medicine_name'],
                        timing,
                        history_id  # Pass the history_id
                    )
                    if sms_sent:
                        logger.info(f"✅ SMS sent to {user['phone']}")
                    else:
                        logger.error(f"❌ Failed to send SMS to {user['phone']}")
                except Exception as e:
                    logger.error(f"SMS sending error: {e}")"""
            
            # Store job reference
            job_id = f"reminder_{history_id}"
            self.scheduled_jobs[job_id] = {
                'medicine': medicine,
                'history_id': history_id,
                'user_id': medicine['user_id'],
                'sent_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Reminder scheduler stopped")
    def schedule_medicine_reminders(self, medicine_data):
        """
        Schedule reminders for a newly added medicine
        This method is called when a new medicine is added
        """
        try:
            logger.info(f"📅 Scheduling reminders for new medicine: {medicine_data.get('medicine_name')}")
            
            # You can add specific scheduling logic here if needed
            # For now, we don't need to do anything special as the 
            # periodic checker will pick it up automatically
            
            # Optionally, you could schedule immediate verification
            # or set up specific jobs for this medicine
            
            return True
        except Exception as e:
            logger.error(f"Error scheduling medicine reminders: {e}")
            return False