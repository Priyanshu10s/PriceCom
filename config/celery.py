import os
import celery
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Infrastructure Handshake
app = Celery('config')

# 3. Force Logic: Read config from Django settings, the CELERY namespace configuration check
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Force Logic: Autodiscover tasks across all installed apps
# This ensures we don't need to manually register tasks.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
