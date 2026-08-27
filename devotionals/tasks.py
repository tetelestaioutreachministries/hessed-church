from celery import shared_task

from .services import send_todays_devotional_push


@shared_task(name="devotionals.tasks.send_daily_devotional_push")
def send_daily_devotional_push():
    """Optional Celery wrapper around send_todays_devotional_push(), kept
    for projects that already run Celery for other reasons. For a
    single daily task like this, a plain cron job calling the
    `send_devotional_push` management command (see devotionals/services.py)
    is simpler and doesn't require Redis/Celery at all."""
    return send_todays_devotional_push()
