from django.db import models


class Devotional(models.Model):
    """A daily devotional. Fully involuntary/automatic on the Flutter side —
    no user action needed, just a scheduled push + auto-fetch."""

    date = models.DateField(unique=True)
    title = models.CharField(max_length=200)
    verse = models.CharField(max_length=255, help_text="e.g. 'Psalm 23:1'")
    content = models.TextField()
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this devotional from the public /devotionals/ page while you're still "
                   "drafting it. It still shows in /manage/ and /admin/ either way.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.title}"
