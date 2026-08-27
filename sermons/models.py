from django.db import models
from django.utils.text import slugify


class Series(models.Model):
    """A sermon series (e.g. a multi-week teaching theme)."""

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="series/", blank=True, null=True)

    video_url = models.URLField(blank=True, help_text="'Watch the Video' link")
    audio_url = models.URLField(blank=True, help_text="'Listen to the Message' link")

    apple_podcast_url = models.URLField("Apple Podcast URL", blank=True)
    spotify_url = models.URLField("Spotify URL", blank=True)
    soundcloud_url = models.URLField("SoundCloud URL", blank=True)
    youtube_url = models.URLField("YouTube URL", blank=True)

    is_current = models.BooleanField(
        default=False,
        help_text="Shown on the homepage 'Current Series' section. Only one series can be current at a time.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "series"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Enforce "only one current series" at the model level so this rule
        # holds no matter how the record is saved (admin, shell, migration, API).
        if self.is_current:
            Series.objects.exclude(pk=self.pk).filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_current=True).first()


class Sermon(models.Model):
    """An individual sermon, belonging to a series."""

    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="sermons")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    speaker = models.CharField(max_length=150)
    date = models.DateField()
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(
        blank=True, help_text="Cloudinary secure_url of the compressed (64kbps) audio. Set automatically on upload."
    )
    notes = models.TextField(blank=True)

    # -- Phase 2: on-demand audio download (Cloudinary-backed) -------------
    thumbnail_url = models.URLField(blank=True)
    file_size_mb = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True,
        help_text="Size of the compressed audio file, shown on the 'Download {size}MB' button.",
    )
    cloudinary_id = models.CharField(
        max_length=255, blank=True, help_text="Cloudinary public_id for the audio, so it can be replaced/deleted."
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this sermon from the public /sermons/ page while you're still "
                   "preparing it (e.g. audio not uploaded yet). It still shows in /manage/ and /admin/ either way.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.speaker})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Sermon.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base_slug}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def download_url(self):
        """audio_url with Cloudinary's fl_attachment flag inserted, so
        clicking the download button actually downloads the file instead of
        opening/playing it inline in the browser."""
        if not self.audio_url:
            return ""
        if "/upload/" in self.audio_url and "fl_attachment" not in self.audio_url:
            return self.audio_url.replace("/upload/", "/upload/fl_attachment/", 1)
        return self.audio_url
