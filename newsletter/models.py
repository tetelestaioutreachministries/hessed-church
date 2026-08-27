import uuid

from django.db import models


class Subscriber(models.Model):
    """A visitor who signed up to be emailed when a new sermon or event is
    posted. unsubscribe_token gives every email a working one-click
    unsubscribe link without requiring the person to log in."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
