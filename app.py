import logging
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

# Configure logging for production
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# ===== Production-Ready Keep-Alive =====
def start_ping_loop():
    """Background thread to ping the app every 30 seconds with proper app context"""
    def ping_server():
        with app.app_context():  # Required for Flask context
            url = "https://analystsameer.onrender.com"
            while True:
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=10)
                    ping_time = (time.time() - start_time) * 1000
                    app.logger.info(
                        f"Keep-alive | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                        f"Status: {response.status_code} | "
                        f"Latency: {ping_time:.2f}ms"
                    )
                except requests.exceptions.RequestException as e:
                    app.logger.error(f"Keep-alive request failed: {str(e)}")
                except Exception as e:
                    app.logger.error(f"Unexpected keep-alive error: {str(e)}")
                finally:
                    time.sleep(30)  # Strict 30-second interval

    if not app.debug:
        thread = threading.Thread(target=ping_server, daemon=True)
        thread.start()
        app.logger.info("Keep-alive service started")

# ===== Application Routes =====
def load_data_from_json(filename):
    """Improved JSON loader with better error handling"""
    data_path = os.path.join(app.root_path, 'data', filename)
    
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        app.logger.warning(f"Data file not found: {filename}")
        return []
    except json.JSONDecodeError as e:
        app.logger.error(f"Invalid JSON in {filename}: {str(e)}")
        return []
    except Exception as e:
        app.logger.error(f"Error loading {filename}: {str(e)}")
        return []

@app.route('/')
def index():
    """Enhanced homepage route with error tracking"""
    try:
        return render_template(
            'index.html',
            certifications=load_data_from_json('certifications.json'),
            experiences=load_data_from_json('experience.json'),
            projects=load_data_from_json('projects.json'),
            skills=load_data_from_json('skills.json')
        )
    except Exception as e:
        app.logger.critical(f"Homepage failed: {str(e)}")
        return render_template('error.html'), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    """More robust contact form handler"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            
            if not all([name, email, message]):
                flash('Please fill in all fields.', 'danger')
                return redirect(url_for('index', _anchor='contact'))
            
            msg = Message(
                subject="New Portfolio Message",
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['RECIPIENT_EMAIL']]
            )
            msg.body = f"""New message from your portfolio:
            
Name: {name}
Email: {email}
Message: 
{message}
            """
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            app.logger.info(f"Contact form submitted by {name}")
            
        except Exception as e:
            app.logger.error(f"Contact failed: {str(e)}")
            flash('Error sending message. Please try again.', 'danger')
        
        return redirect(url_for('index', _anchor='contact'))

# ===== Startup Configuration =====
if __name__ == '__main__':
    # Local development configuration
    start_ping_loop()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 3000)),
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )
else:
    # Production configuration
    start_ping_loop()