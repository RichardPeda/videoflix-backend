from __future__ import absolute_import, unicode_literals

# Damit Celery beim Django-Start geladen wird
from .celery import app as celery_app

__all__ = ('celery_app',)