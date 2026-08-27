from django.conf import settings
from django.db import models


class ConnectGroup(models.Model):
    name = models.CharField(max_length=200)
    leader_name = models.CharField(max_length=150)
    leader_email = models.EmailField(blank=True, help_text="If left blank, inquiries route to the general church email.")
    meeting_day = models.CharField(max_length=50, blank=True)
    meeting_time = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GroupInquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    facebook = models.CharField("Facebook URL", max_length=255, blank=True)
    age = models.CharField(max_length=20, blank=True)
    availability = models.CharField(max_length=255, blank=True, help_text="Day & time available")
    group = models.ForeignKey(
        ConnectGroup, on_delete=models.SET_NULL, blank=True, null=True, related_name="inquiries"
    )
    comments = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "group inquiries"

    def __str__(self):
        return f"{self.name} -> {self.group or 'unspecified group'}"

    @property
    def recipient_email(self):
        """Route to the chosen group's leader, falling back to the general church email."""
        if self.group and self.group.leader_email:
            return self.group.leader_email
        return settings.CHURCH_GENERAL_EMAIL
