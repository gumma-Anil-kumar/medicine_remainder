from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from datetime import datetime
import logging

from config import Config
from utils.database import MongoDB
from utils.reminder_scheduler import ReminderScheduler
from utils.notification import NotificationService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize database
db = MongoDB()

# Initialize services
notification_service = NotificationService()
notification_service.init_mail(app)  # Initialize mail with app

# Initialize scheduler with app context
reminder_scheduler = ReminderScheduler(app, db, notification_service)
reminder_scheduler.start()

# ... rest of your routes remain the same
# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data.get('name', '')
        self.email = user_data.get('email', '')
        self.phone = user_data.get('phone', '')
        self.notification_preferences = user_data.get('notification_preferences', {
            'email': True,
            'sms': False,
            'call': False
        })

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(ObjectId(user_id))
    return User(user_data) if user_data else None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        # Check if user exists
        if db.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create user document
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'notification_preferences': {
                'email': True,
                'sms': False,
                'call': False
            },
            'created_at': datetime.now()
        }
        
        db.create_user(user_data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = db.get_user_by_email(email)
        
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    medicines = db.get_user_medicines(ObjectId(current_user.id))
    
    # Get today's medicines
    current_day = datetime.now().strftime('%a').lower()[:3]
    today_medicines = []
    
    for med in medicines:
        if current_day in med.get('days', {}):
            today_medicines.append({
                '_id': med['_id'],  # Add this line - include the ID
                'name': med['medicine_name'],
                'timings': med['days'][current_day],
                'taken_status': get_today_status(med['_id'])
            })
    
    return render_template('dashboard.html', 
                         medicines=medicines, 
                         today_medicines=today_medicines)

def get_today_status(medicine_id):
    """Check if medicine was taken today"""
    today = datetime.now().strftime('%Y-%m-%d')
    history_entry = db.history.find_one({
        'medicine_id': medicine_id,
        'date': today
    })
    return history_entry['status'] if history_entry else 'pending'

@app.route('/add_medicine', methods=['GET', 'POST'])
@login_required
def add_medicine():
    if request.method == 'POST':
        try:
            medicine_name = request.form.get('medicine_name')
            description = request.form.get('description')
            
            # Parse days and timings
            days = {}
            for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                if request.form.get(f'day_{day}'):
                    timings = request.form.getlist(f'timings_{day}[]')
                    # Filter out empty strings
                    timings = [t for t in timings if t]
                    if timings:  # Only add if there are timings
                        days[day] = timings
            
            # Validate that at least one day is selected
            if not days:
                flash('Please select at least one day and add timings', 'danger')
                return redirect(url_for('add_medicine'))
            
            # Handle image upload
            image_file = request.files.get('medicine_image')
            image_path = None
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                # Add timestamp to avoid filename conflicts
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                
                # Ensure upload directory exists
                upload_dir = os.path.join(app.static_folder, 'uploads/medicine_images')
                os.makedirs(upload_dir, exist_ok=True)
                
                image_path = os.path.join('uploads/medicine_images', filename)
                image_file.save(os.path.join(app.static_folder, image_path))
            
            medicine_data = {
                'user_id': ObjectId(current_user.id),
                'medicine_name': medicine_name,
                'description': description,
                'days': days,
                'image_path': image_path,
                'created_at': datetime.now()
            }
            
            # Add to database
            result = db.add_medicine(medicine_data)
            
            # Schedule reminders (method now exists)
            try:
                reminder_scheduler.schedule_medicine_reminders(medicine_data)
            except Exception as e:
                logger.error(f"Error in scheduling: {e}")
                # Don't fail the whole request if scheduling fails
                pass
            
            flash(f'Medicine "{medicine_name}" added successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Error adding medicine: {e}")
            flash(f'Error adding medicine: {str(e)}', 'danger')
            return redirect(url_for('add_medicine'))
    
    return render_template('add_medicine.html')
@app.route('/medicines')
@login_required
def medicine_list():
    medicines = db.get_user_medicines(ObjectId(current_user.id))
    return render_template('medicine_list.html', medicines=medicines)

@app.route('/medicine/<medicine_id>/delete')
@login_required
def delete_medicine(medicine_id):
    db.delete_medicine(ObjectId(medicine_id))
    flash('Medicine deleted successfully', 'success')
    return redirect(url_for('medicine_list'))

@app.route('/history')
@login_required
def history():
    user_history = db.history.find({
        'user_id': ObjectId(current_user.id)
    }).sort('date', -1).sort('time', -1)
    
    return render_template('history.html', history=user_history)

@app.route('/api/notification/<history_id>/<action>', methods=['POST'])
@login_required
def handle_notification(history_id, action):
    """Handle notification actions (taken/snooze)"""
    if action == 'taken':
        db.update_history_entry(
            ObjectId(history_id),
            {'status': 'taken', 'taken_time': datetime.now()}
        )
        return jsonify({'success': True, 'message': 'Medicine marked as taken'})
    
    elif action == 'snooze':
        # Create snooze logic here (e.g., remind after 15 minutes)
        return jsonify({'success': True, 'message': 'Snoozed for 15 minutes'})
    
    return jsonify({'success': False, 'message': 'Invalid action'})

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Update notification preferences
        preferences = {
            'email': request.form.get('email_notif') == 'on',
            'sms': False,
            'call': False
        }
        
        db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': {'notification_preferences': preferences}}
        )
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('settings'))
    
    user_data = db.get_user_by_id(ObjectId(current_user.id))
    return render_template('settings.html', 
                         preferences=user_data.get('notification_preferences', {}))
@app.route('/test-reminder-now')
@login_required
def test_reminder_now():
    """Manually trigger a reminder for testing"""
    try:
        # Get user's medicines
        medicines = db.get_user_medicines(ObjectId(current_user.id))
        
        if not medicines:
            flash('No medicines found to test', 'warning')
            return redirect(url_for('dashboard'))
        
        # Use the first medicine
        medicine = medicines[0]
        current_time = datetime.now().strftime('%H:%M')
        
        # Send test email
        result = notification_service.send_email_reminder(
            current_user.email,
            medicine['medicine_name'],
            current_time
        )
        
        if result:
            flash(f'Test reminder sent for {medicine["medicine_name"]}! Check your email.', 'success')
        else:
            flash('Failed to send test reminder. Check logs.', 'danger')
            
    except Exception as e:
        logger.error(f"Test reminder error: {e}")
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))
@app.route('/mark-taken/<history_id>')
def mark_taken_from_email(history_id):
    """Route for marking medicine as taken from email link"""
    try:
        # Update the history entry
        result = db.history.update_one(
            {'_id': ObjectId(history_id)},
            {
                '$set': {
                    'status': 'taken',
                    'taken_time': datetime.now(),
                    'taken_from_email': True
                }
            }
        )
        
        if result.modified_count > 0:
            # Get the history entry to show medicine name
            history = db.history.find_one({'_id': ObjectId(history_id)})
            
            # Return a nice confirmation page
            return render_template('taken_confirmation.html', 
                                 medicine_name=history.get('medicine_name'),
                                 time=history.get('time'))
        else:
            return render_template('taken_confirmation.html', 
                                 error="Could not update status. The reminder might have been already marked as taken.")
            
    except Exception as e:
        logger.error(f"Error marking medicine as taken: {e}")
        return render_template('taken_confirmation.html', 
                             error="An error occurred. Please try again.")
@app.route('/edit-medicine/<medicine_id>', methods=['GET', 'POST'])
@login_required
def edit_medicine(medicine_id):
    """Edit an existing medicine"""
    try:
        # Get the medicine
        medicine = db.medicines.find_one({'_id': ObjectId(medicine_id)})
        
        # Check if medicine exists and belongs to current user
        if not medicine:
            flash('Medicine not found', 'danger')
            return redirect(url_for('medicine_list'))
        
        if medicine['user_id'] != ObjectId(current_user.id):
            flash('You do not have permission to edit this medicine', 'danger')
            return redirect(url_for('medicine_list'))
        
        if request.method == 'POST':
            # Get form data
            medicine_name = request.form.get('medicine_name')
            description = request.form.get('description')
            
            # Parse days and timings
            days = {}
            for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                if request.form.get(f'day_{day}'):
                    timings = request.form.getlist(f'timings_{day}[]')
                    timings = [t for t in timings if t]  # Remove empty strings
                    if timings:
                        days[day] = timings
            
            if not days:
                flash('Please select at least one day and add timings', 'danger')
                return redirect(url_for('edit_medicine', medicine_id=medicine_id))
            
            # Handle image upload
            image_file = request.files.get('medicine_image')
            image_path = medicine.get('image_path')  # Keep old image by default
            
            if image_file and image_file.filename:
                # Delete old image if exists
                if image_path:
                    old_image_path = os.path.join(app.static_folder, image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Save new image
                filename = secure_filename(image_file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                
                upload_dir = os.path.join(app.static_folder, 'uploads/medicine_images')
                os.makedirs(upload_dir, exist_ok=True)
                
                image_path = os.path.join('uploads/medicine_images', filename)
                image_file.save(os.path.join(app.static_folder, image_path))
            
            # Update medicine in database
            update_data = {
                'medicine_name': medicine_name,
                'description': description,
                'days': days,
                'image_path': image_path,
                'updated_at': datetime.now()
            }
            
            db.medicines.update_one(
                {'_id': ObjectId(medicine_id)},
                {'$set': update_data}
            )
            
            flash(f'Medicine "{medicine_name}" updated successfully!', 'success')
            return redirect(url_for('medicine_list'))
        
        # GET request - show edit form
        return render_template('edit_medicine.html', medicine=medicine)
        
    except Exception as e:
        logger.error(f"Error editing medicine: {e}")
        flash(f'Error editing medicine: {str(e)}', 'danger')
        return redirect(url_for('medicine_list'))

if __name__ == '__main__':
    app.run(debug=True)