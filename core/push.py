"""
Thin wrapper around firebase-admin for sending FCM pushes.

Initialized lazily from a service account JSON whose path is given by the
FIREBASE_SERVICE_ACCOUNT_JSON environment variable (kept out of version
control). If that variable isn't set (e.g. local dev without Firebase
configured), push calls are silently skipped so the rest of the app keeps
working.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_firebase_app = None
_INIT_ATTEMPTED = False


def _get_firebase_app():
    global _firebase_app, _INIT_ATTEMPTED
    if _firebase_app is not None or _INIT_ATTEMPTED:
        return _firebase_app
    _INIT_ATTEMPTED = True

    if not settings.FIREBASE_SERVICE_ACCOUNT_JSON:
        logger.warning("FIREBASE_SERVICE_ACCOUNT_JSON not set — FCM pushes are disabled.")
        return None

    import firebase_admin
    from firebase_admin import credentials

    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
    _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def send_push_to_tokens(tokens, title, body, data=None):
    """Sends the same notification to a list of FCM device tokens.
    Silently no-ops if Firebase isn't configured (dev) or the token list is empty."""
    tokens = list(tokens)
    if not tokens:
        return

    app = _get_firebase_app()
    if app is None:
        logger.info("Skipping FCM push (not configured): %s / %s", title, body)
        return

    from firebase_admin import messaging

    # FCM's multicast endpoint caps out at 500 tokens per call.
    for i in range(0, len(tokens), 500):
        batch = tokens[i : i + 500]
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            tokens=batch,
        )
        try:
            response = messaging.send_each_for_multicast(message, app=app)
            logger.info("FCM push sent: %s succeeded, %s failed", response.success_count, response.failure_count)
        except Exception:
            logger.exception("FCM push failed")


def send_push_to_all_devices(title, body, data=None):
    from core.models import DeviceToken

    tokens = DeviceToken.objects.values_list("token", flat=True)
    send_push_to_tokens(tokens, title, body, data=data)
