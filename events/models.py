from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    summary = models.TextField(help_text="Short summary shown on list pages.")
    description = models.TextField(
        blank=True,
        help_text="Full description for the event detail page. Falls back to the summary if left blank.",
    )
    image = models.ImageField(upload_to="events/", blank=True, null=True)

    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    age_group = models.CharField(max_length=100, blank=True, help_text="e.g. '7-12 Years Old'")
    cost = models.CharField(max_length=100, blank=True, help_text="e.g. '150 USD' or 'Free'")

    is_published = models.BooleanField(default=True)

    # -- Phase 2: poster upload / sharing (Cloudinary-backed) --------------
    poster_url = models.URLField(
        blank=True, help_text="Cloudinary secure_url of the compressed poster. Set automatically on upload."
    )
    cloudinary_id = models.CharField(
        max_length=255, blank=True, help_text="Cloudinary public_id for the poster, so it can be replaced/deleted."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base_slug}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"slug": self.slug})

    @property
    def display_description(self):
        return self.description or self.summary

    @property
    def time_range_display(self):
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%I:%M%p').lstrip('0')} - {self.end_time.strftime('%I:%M%p').lstrip('0')}"
        if self.start_time:
            return self.start_time.strftime("%I:%M%p").lstrip("0")
        return ""


class EventRSVP(models.Model):
    """
    Through-model for event RSVPs (rather than a plain M2M) so each RSVP has
    a timestamp and the API endpoint can be idempotent (get_or_create).
    """

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_rsvps")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.event}"
