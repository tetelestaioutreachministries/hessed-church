import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hesed_church.settings")

app = Celery("hesed_church")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Daily devotional push — 6:00 AM Africa/Kampala (CELERY_TIMEZONE is set to
# Africa/Kampala in settings.py, so this crontab is already in that zone).
app.conf.beat_schedule = {
    "send-daily-devotional-push": {
        "task": "devotionals.tasks.send_daily_devotional_push",
        "schedule": crontab(hour=6, minute=0),
    },
}
