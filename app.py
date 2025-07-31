from flask import Flask, render_template, request, flash, redirect, url_for
import json
import os
from flask_mail import Mail, Message
import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['SECRET_KEY']

# Initialize Flask-Mail
mail = Mail(app)

def load_data_from_json(filename):
    """Helper function to load data from JSON files"""
    data_path = os.path.join(app.root_path, 'data', filename)
    try:
        with open(data_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Returning empty list.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON. Returning empty list.")
        return []

# Set up routes
@app.route('/')
def index():
    # Load all data from JSON files
    certifications = load_data_from_json('certifications.json')
    experiences = load_data_from_json('experience.json')
    projects = load_data_from_json('projects.json')
    skills = load_data_from_json('skills.json')
    
    return render_template('index.html',
                           certifications=certifications,
                           experiences=experiences,
                           projects=projects,
                           skills=skills)

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Send email notification
        try:
            msg = Message("New Message From Portfolio",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['RECIPIENT_EMAIL']])
            msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
            mail.send(msg)
            flash('Message sent successfully! I will get back to you soon.', 'success')
        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'danger')
        
        return redirect(url_for('index', _anchor='contact'))

if __name__ == '__main__':
    app.run(debug=True)