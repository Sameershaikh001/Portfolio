import os

# Gunicorn config for Render deployment
bind = f"0.0.0.0:{os.environ.get('PORT', '3000')}"
workers = 2
threads = 4
worker_class = "gthread"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging configuration
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stdout
loglevel = "info"