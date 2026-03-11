# 💊 Medicine Reminder App for Elderly

A thoughtful Flask-based web application designed to help elderly people never miss their medications. The app sends email reminders with clickable confirmation buttons and maintains a complete history of medicine intake.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)
![Railway](https://img.shields.io/badge/Railway-Deployed-purple.svg)

## ✨ Features

- **👤 User Authentication** - Secure registration and login system
- **💊 Medicine Management** - Add, edit, and delete medicines with custom schedules
- **📧 Email Reminders** - Automatic reminders at scheduled times
- **✅ One-Click Confirmation** - Email buttons to mark medicines as taken
- **📊 History Tracking** - Complete log of all reminders and responses
- **📱 Mobile Responsive** - Works perfectly on phones and tablets
- **🎯 Elderly-Friendly UI** - Large buttons, clear fonts, simple navigation

## 🖼️ Screenshots

*[Add screenshots of your app here after deployment]*

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Web framework |
| **MongoDB Atlas** | Cloud database |
| **Flask-Mail** | Email notifications |
| **APScheduler** | Background reminders |
| **Bootstrap 5** | Responsive UI |
| **Jinja2** | HTML templating |
| **Railway** | Hosting platform |

## 🚀 Live Demo

**Visit the live app:** [https://medicine-reminder.up.railway.app](https://medicine-reminder.up.railway.app)

*Note: First visit may be slow as the free tier spins up after inactivity.*

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.8+ installed
- MongoDB Atlas account (free tier)
- Gmail account (for email notifications)

## 🔧 Local Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/medicine-reminder-flask.git
cd medicine-reminder-flask
Create virtual environment
bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Set up environment variables
Create a .env file in the root directory:

env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/medicine_reminder
DB_NAME=medicine_reminder
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
SERVER_NAME=127.0.0.1:5000
PREFERRED_URL_SCHEME=http
5. Run the application
bash
python app.py
Visit http://127.0.0.1:5000 in your browser.

📧 Gmail Setup for Email Reminders
Enable 2-Factor Authentication in your Google account

Generate an App Password:

Google Account → Security → App Passwords

Select "Mail" and "Other" (name it "Medicine Reminder")

Copy the 16-character password

Use this password in your .env
