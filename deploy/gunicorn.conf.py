# Gunicorn configuration file for F1 Fantasy Test Stack
import multiprocessing
import os

# Server socket - Bind to all interfaces for easy access
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - Reduced for test environment
workers = max(2, multiprocessing.cpu_count())
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/f1fantasy/gunicorn_access.log"
errorlog = "/var/log/f1fantasy/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "f1fantasy-test"

# Daemon mode
daemon = False
pidfile = "/var/run/f1fantasy.pid"

# User/group to run as
user = "f1fantasy"
group = "f1fantasy"

# Temporary directory
tmp_upload_dir = "/tmp"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if you want to terminate SSL at Gunicorn instead of nginx)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    "FLASK_ENV=testing",
]

# Preload app for better memory usage
preload_app = True

def when_ready(server):
    server.log.info("F1 Fantasy Test Stack is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid) 