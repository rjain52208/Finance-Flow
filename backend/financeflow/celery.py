"""
Celery configuration for financeflow project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeflow.settings')

app = Celery('financeflow')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule - for periodic tasks
app.conf.beat_schedule = {
    'send-daily-budget-summary': {
        'task': 'tasks.tasks.send_daily_budget_summary',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'send-weekly-report': {
        'task': 'tasks.tasks.send_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Every Monday at 9 AM
    },
    'send-monthly-report': {
        'task': 'tasks.tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # First day of month at 9 AM
    },
    'check-budget-alerts': {
        'task': 'tasks.tasks.check_budget_alerts',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
