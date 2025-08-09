from flask import Flask, render_template, request, flash, redirect, url_for
import json
import os
from flask_mail import Mail, Message
import config
import threading
import requests
import time
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(config)

# Set secret key for session management and flash messages
app.secret_key = app.config['SECRET_KEY']

# Initialize Flask-Mail for email functionality
mail = Mail(app)

# ===== Enhanced Keep-Alive Functionality =====
def start_ping_loop():
    """Background thread to ping the app every 30 seconds with improved error handling"""
    def ping_server():
        url = "https://analystsameer.onrender.com"  # Your Render URL
        while True:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                ping_time = (time.time() - start_time) * 1000
                app.logger.info(
                    f"Keep-alive | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"URL: {url} | Status: {response.status_code} | "
                    f"Latency: {ping_time:.2f}ms"
                )
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Keep-alive failed: {str(e)}")
            except Exception as e:
                app.logger.error(f"Unexpected keep-alive error: {str(e)}")
            
            time.sleep(30)  # 30-second interval

    if not app.debug:  # Only start in production
        thread = threading.Thread(target=ping_server, daemon=True)
        thread.start()
        app.logger.info("Keep-alive thread started")
# ===== END Keep-Alive =====

def load_data_from_json(filename):
    """Helper function to safely load data from JSON files"""
    data_path = os.path.join(app.root_path, 'data', filename)
    
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        app.logger.warning(f"{filename} not found in data directory")
        return []
    except json.JSONDecodeError as e:
        app.logger.error(f"Invalid JSON in {filename}: {str(e)}")
        return []
    except Exception as e:
        app.logger.error(f"Error loading {filename}: {str(e)}")
        return []

@app.route('/')
def index():
    """Main route that serves the portfolio homepage"""
    certifications = load_data_from_json('certifications.json')
    experiences = load_data_from_json('experience.json')
    projects = load_data_from_json('projects.json')
    skills = load_data_from_json('skills.json')
    
    return render_template(
        'index.html',
        certifications=certifications,
        experiences=experiences,
        projects=projects,
        skills=skills
    )

@app.route('/send_message', methods=['POST'])
def send_message():
    """Handles contact form submissions"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if not all([name, email, message]):
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('index', _anchor='contact'))
        
        try:
            msg = Message(
                subject="New Message From Your Portfolio",
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['RECIPIENT_EMAIL']]
            )
            msg.body = f"""New message from your portfolio website:
            
Name: {name}
Email: {email}
Message: 
{message}
            """
            mail.send(msg)
            flash('Message sent successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Email failed: {str(e)}")
            flash('Error sending message. Please try again.', 'danger')
        
        return redirect(url_for('index', _anchor='contact'))

def send_sms_notification(name, email):
    """Optional SMS notifications via Twilio"""
    if all([app.config.get('TWILIO_ACCOUNT_SID'), 
            app.config.get('TWILIO_AUTH_TOKEN'),
            app.config.get('TWILIO_PHONE_NUMBER'),
            app.config.get('RECIPIENT_PHONE_NUMBER')]):
        try:
            from twilio.rest import Client
            client = Client(app.config['TWILIO_ACCOUNT_SID'], 
                         app.config['TWILIO_AUTH_TOKEN'])
            message = client.messages.create(
                body=f"New message from {name} ({email})",
                from_=app.config['TWILIO_PHONE_NUMBER'],
                to=app.config['RECIPIENT_PHONE_NUMBER']
            )
            app.logger.info(f"SMS notification sent: {message.sid}")
        except Exception as e:
            app.logger.error(f"SMS failed: {str(e)}")

if __name__ == '__main__':
    # Initialize keep-alive
    start_ping_loop()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 3000)),
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )