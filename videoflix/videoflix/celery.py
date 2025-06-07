import os
from celery import Celery

"""
Celery application configuration for the Videoflix project.

This module sets the default Django settings module for the 'celery' command-line program.
It then creates a Celery application instance and configures it using Django's settings
under the CELERY namespace. It also automatically discovers asynchronous task modules
in all installed Django apps.

Usage:
    This module is imported in the __init__.py of the Django project package
    to ensure the Celery app is loaded when Django starts.

Example:
    To start a worker:
        celery -A videoflix worker --loglevel=info
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "videoflix.settings")
app = Celery("videoflix")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()