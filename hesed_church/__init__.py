# Celery is optional for this project — the only thing it was scheduling
# (the daily devotional push) now runs via a plain cron job calling
# `python manage.py send_devotional_push` (see devotionals/services.py).
# If you later add Celery back for other background work, this import
# wires it up automatically; until then, missing the celery package
# doesn't break anything.
try:
    from .celery import app as celery_app
    __all__ = ("celery_app",)
except ImportError:
    pass
