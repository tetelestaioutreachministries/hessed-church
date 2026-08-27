from django.contrib import admin

from .models import ConnectGroup, GroupInquiry


@admin.register(ConnectGroup)
class ConnectGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "leader_name", "leader_email", "meeting_day", "meeting_time", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "leader_name")


@admin.register(GroupInquiry)
class GroupInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "group", "created_at", "is_handled")
    list_filter = ("is_handled", "group")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
