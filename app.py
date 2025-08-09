from flask import Flask, render_template, request, flash, redirect, url_for
import json
import os
from flask_mail import Mail, Message
import config
import threading  # For background ping
import requests   # For HTTP requests
import time       # For sleep interval
from datetime import datetime  # For timestamps

# Initialize Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(config)

# Set secret key for session management and flash messages
app.secret_key = app.config['SECRET_KEY']

# Initialize Flask-Mail for email functionality
mail = Mail(app)

# ===== Keep-Alive Functionality =====
def start_ping_loop():
    """Background thread to ping the app every 30 seconds"""
    def ping_server():
        url = "https://analystsameer.onrender.com"  # REPLACE WITH YOUR RENDER URL
        while True:
            try:
                start_time = time.time()
                response = requests.get(url)
                ping_time = (time.time() - start_time) * 1000  # Calculate ping time in ms
                # Replace print() with app.logger in your ping function:
                app.logger.info(f"{datetime.now()} | Keep-alive ping to {url} | Status: {response.status_code}")
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Keep-alive failed: {str(e)}")
            time.sleep(30)  # 30-second interval between pings

    # Start the thread (daemon=True allows it to exit with main thread)
    thread = threading.Thread(target=ping_server, daemon=True)
    thread.start()
# ===== END Keep-Alive =====

def load_data_from_json(filename):
    """
    Helper function to safely load data from JSON files
    Args:
        filename (str): Name of the JSON file to load (e.g., 'projects.json')
    Returns:
        list: Loaded data or empty list if file not found/invalid
    """
    data_path = os.path.join(app.root_path, 'data', filename)
    
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: {filename} not found in data directory. Using empty list.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filename}. Error: {str(e)}. Using empty list.")
        return []
    except Exception as e:
        print(f"Unexpected error loading {filename}: {str(e)}. Using empty list.")
        return []

@app.route('/')
def index():
    """
    Main route that serves the portfolio homepage
    Loads all data from JSON files and passes it to the template
    """
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
    """
    Handles form submission from the contact section
    Processes the message and sends email notifications
    """
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
            msg.body = f"""
            New message from your portfolio website:
            
            Name: {name}
            Email: {email}
            Message: 
            {message}
            """
            
            mail.send(msg)
            flash('Your message has been sent successfully! I will get back to you soon.', 'success')
            
        except Exception as e:
            app.logger.error(f"Failed to send email: {str(e)}")
            flash('Sorry, there was an error sending your message. Please try again later.', 'danger')
        
        return redirect(url_for('index', _anchor='contact'))

def send_sms_notification(name, email):
    """
    Optional function to send SMS notification (requires Twilio setup)
    """
    if all([app.config.get('TWILIO_ACCOUNT_SID'), 
            app.config.get('TWILIO_AUTH_TOKEN'),
            app.config.get('TWILIO_PHONE_NUMBER'),
            app.config.get('RECIPIENT_PHONE_NUMBER')]):
        
        try:
            from twilio.rest import Client
            client = Client(app.config['TWILIO_ACCOUNT_SID'], 
                           app.config['TWILIO_AUTH_TOKEN'])
            
            message = client.messages.create(
                body=f"New portfolio message from {name} ({email})",
                from_=app.config['TWILIO_PHONE_NUMBER'],
                to=app.config['RECIPIENT_PHONE_NUMBER']
            )
            app.logger.info(f"SMS sent: {message.sid}")
        except Exception as e:
            app.logger.error(f"Failed to send SMS: {str(e)}")

if __name__ == '__main__':
    # Start keep-alive thread
    start_ping_loop()
    
    # Run the application
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))