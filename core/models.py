from django.conf import settings
from django.db import models


class Profile(models.Model):
    """
    One-to-one extension of the default auth.User, used instead of a custom
    AUTH_USER_MODEL because Phase 1 migrations already exist against the
    default user model — swapping AUTH_USER_MODEL now would require a full
    database reset. This is the safer path for a project already running.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    google_sub = models.CharField(
        max_length=255, blank=True, unique=True, null=True,
        help_text="Google account subject ('sub') claim from the verified idToken.",
    )
    avatar_url = models.URLField(blank=True)
    saved_sermons = models.ManyToManyField("sermons.Sermon", blank=True, related_name="saved_by")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_username()


class DeviceToken(models.Model):
    """An FCM registration token for a Flutter device. user is nullable so
    anonymous devices can still receive the daily devotional push."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="device_tokens"
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token[:16]}... ({self.user or 'anonymous'})"
