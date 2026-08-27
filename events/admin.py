from django.contrib import admin, messages

from .forms import EventPosterUploadForm
from .models import Event, EventRSVP

class EventRSVPInline(admin.TabularInline):
    model = EventRSVP
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "location")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "date"
    readonly_fields = ("poster_url", "cloudinary_id")
    inlines = [EventRSVPInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "image", "is_published")}),
        ("Content", {"fields": ("summary", "description")}),
        ("Details", {"fields": ("date", "start_time", "end_time", "location", "age_group", "cost")}),
        (
            "Poster (Cloudinary)",
            {
                "fields": ("poster_file_upload", "poster_url", "cloudinary_id"),
                "description": "Upload a poster JPG below — it's resized (max 1080x1920), compressed "
                               "under 300KB, and uploaded to Cloudinary automatically.",
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        class FormWithUpload(form):
            poster_file_upload = EventPosterUploadForm.base_fields["poster_file"]

        return FormWithUpload

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        uploaded_file = form.cleaned_data.get("poster_file_upload")

        if uploaded_file:
            upload_form = EventPosterUploadForm(files={"poster_file": uploaded_file})
            if upload_form.is_valid():
                result = upload_form.process_and_upload()
                if result:
                    obj.poster_url, obj.cloudinary_id = result
                    messages.success(request, "Poster uploaded to Cloudinary.")

        super().save_model(request, obj, form, change)

        if is_new and obj.is_published:
            from newsletter.services import notify_new_event
            notify_new_event(obj, request=request)
