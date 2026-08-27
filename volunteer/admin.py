from django.contrib import admin

from .models import Department, VolunteerApplication


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "contact_email", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name",)


@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department", "is_first_time", "created_at", "is_handled")
    list_filter = ("is_handled", "department", "is_first_time")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
