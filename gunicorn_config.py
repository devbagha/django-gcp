# Gunicorn configuration file
import multiprocessing

# Bind to this socket
bind = "0.0.0.0:8000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class to use
worker_class = "sync"

# Timeout for worker processes
timeout = 120

# The maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Log settings
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr

# Process name
proc_name = "django_gcp"

# Django WSGI application path
wsgi_app = "config.wsgi:application"