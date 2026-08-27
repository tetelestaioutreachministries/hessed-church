from django.contrib import admin

from .models import DeviceToken, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "google_sub", "created_at")
    search_fields = ("user__username", "user__email", "google_sub")
    filter_horizontal = ("saved_sermons",)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user", "created_at")
    search_fields = ("token",)
