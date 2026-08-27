from django.utils import timezone

from core.push import send_push_to_all_devices

from .models import Devotional


def send_todays_devotional_push():
    """Sends today's devotional as an FCM push to every registered device.
    No Celery/Redis required — this is a plain function meant to be called
    once a day by a cron job (see the send_devotional_push management
    command), or from a Celery task if you later add Celery for other work."""
    today = timezone.localdate()
    devotional = Devotional.objects.filter(date=today, is_published=True).first()
    if not devotional:
        return "No devotional published for today — nothing sent."

    send_push_to_all_devices(
        title=f"Today's Devotional: {devotional.title}",
        body=devotional.verse,
        data={"type": "devotional", "date": str(devotional.date)},
    )
    return f"Devotional push sent for {today}"
