"""Gunicorn settings for Cloud Run and other production hosts."""
import os

bind = "0.0.0.0:" + os.environ.get("PORT", "8080")
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
threads = int(os.environ.get("GUNICORN_THREADS", "8"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
worker_class = "gthread"
accesslog = "-"
errorlog = "-"
capture_output = True
