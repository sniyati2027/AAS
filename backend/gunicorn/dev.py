# gunicorn/dev.py
"""Gunicorn *development* config file

Development settings optimized for local development:
- Single worker for simplicity
- Hot reload enabled
- Longer timeout for debugging
"""

import os

# FastAPI ASGI application path
wsgi_app = "app.main:app"

# Logging
loglevel = "info"
accesslog = errorlog = "-"  # Log to stdout for Docker
capture_output = True

# Single worker for development (avoids race conditions)
workers = 1

# Worker class for ASGI support
worker_class = "uvicorn.workers.UvicornWorker"

# Max simultaneous connections per worker
worker_connections = 1000

# Server socket
bind = f"{os.getenv('INTERNAL_IP', '0.0.0.0')}:8000"

# Hot reload on code changes
# Set to False if auto-restarts are disruptive during active development
reload = False  # Changed to prevent connection drops

# Longer timeout for debugging
timeout = 5000

# PID file
pidfile = "/tmp/gunicorn_dev.pid"

# Don't daemonize
daemon = False
