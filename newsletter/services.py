from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import Subscriber


def _absolute_url(path, request=None):
    """Builds a full URL for links inside emails. Uses the current request
    when available (accurate scheme/host); falls back to SITE_BASE_URL
    (set this env var in production) for callers without a request, e.g. a
    cron job or shell command."""
    if request is not None:
        return request.build_absolute_uri(path)
    base = getattr(settings, "SITE_BASE_URL", "http://localhost:8000")
    return f"{base.rstrip('/')}{path}"


def _send_to_active_subscribers(subject, build_body):
    """build_body(unsubscribe_url) -> str, so each email gets its own
    working unsubscribe link."""
    subscribers = Subscriber.objects.filter(is_active=True)
    for subscriber in subscribers:
        unsubscribe_path = reverse("newsletter:unsubscribe", args=[subscriber.unsubscribe_token])
        unsubscribe_url = _absolute_url(unsubscribe_path)
        send_mail(
            subject=subject,
            message=build_body(unsubscribe_url),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=True,
        )


def notify_new_event(event, request=None):
    """Call this once, right when a new published Event is created — not on
    every edit, or subscribers get an email every time staff tweaks a typo."""
    url = _absolute_url(reverse("events:detail", args=[event.slug]), request)

    def build_body(unsubscribe_url):
        return (
            f"A new event was just posted at {settings.CHURCH_NAME}:\n\n"
            f"{event.title}\n"
            f"{event.date.strftime('%A, %B %d, %Y')}"
            f"{' · ' + event.location if event.location else ''}\n\n"
            f"{event.summary}\n\n"
            f"See details: {url}\n\n"
            f"---\n"
            f"You're receiving this because you signed up for updates from {settings.CHURCH_NAME}.\n"
            f"Unsubscribe: {unsubscribe_url}"
        )

    _send_to_active_subscribers(f"New Event: {event.title}", build_body)


def notify_new_sermon(sermon, request=None):
    """Call this when a sermon first becomes 'complete' — i.e. it just got
    its audio uploaded or a video URL set — not on every edit."""
    url = _absolute_url(reverse("sermons:detail", args=[sermon.slug]), request)

    def build_body(unsubscribe_url):
        return (
            f"A new sermon is now available at {settings.CHURCH_NAME}:\n\n"
            f"{sermon.title}\n"
            f"{sermon.speaker} · {sermon.date.strftime('%A, %B %d, %Y')}\n\n"
            f"Watch or download it here: {url}\n\n"
            f"---\n"
            f"You're receiving this because you signed up for updates from {settings.CHURCH_NAME}.\n"
            f"Unsubscribe: {unsubscribe_url}"
        )

    _send_to_active_subscribers(f"New Sermon: {sermon.title}", build_body)
