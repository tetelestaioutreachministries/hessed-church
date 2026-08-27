from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    contact_name = models.CharField(max_length=150, blank=True)
    contact_email = models.EmailField(
        blank=True, help_text="Left blank? Applications route to the general church email instead."
    )
    order = models.PositiveIntegerField(default=0, help_text="Controls display order on the volunteer page.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def recipient_email(self):
        return self.contact_email or settings.CHURCH_GENERAL_EMAIL


class VolunteerApplication(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    facebook = models.CharField("Facebook URL", max_length=255, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="applications")
    is_first_time = models.BooleanField(default=True, verbose_name="First time to serve?")
    comments = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} -> {self.department}"
