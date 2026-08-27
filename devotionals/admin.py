from django.contrib import admin

from .models import Devotional


@admin.register(Devotional)
class DevotionalAdmin(admin.ModelAdmin):
    list_display = ("date", "title", "verse", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "verse", "content")
    date_hierarchy = "date"
