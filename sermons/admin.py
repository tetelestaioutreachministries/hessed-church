from django.contrib import admin, messages

from .forms import SermonAudioUploadForm
from .models import Sermon, Series


class SermonInline(admin.TabularInline):
    model = Sermon
    extra = 0
    fields = ("title", "speaker", "date", "video_url", "audio_url", "file_size_mb")
    readonly_fields = ("audio_url", "file_size_mb")


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("title", "is_current", "created_at")
    list_filter = ("is_current",)
    search_fields = ("title", "subtitle")
    inlines = [SermonInline]
    fieldsets = (
        (None, {"fields": ("title", "subtitle", "description", "image", "is_current")}),
        ("Watch / Listen", {"fields": ("video_url", "audio_url")}),
        (
            "Subscribe links",
            {"fields": ("apple_podcast_url", "spotify_url", "soundcloud_url", "youtube_url")},
        ),
    )


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ("title", "series", "speaker", "date", "file_size_mb", "is_published")
    list_filter = ("series", "is_published")
    search_fields = ("title", "speaker")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "date"
    readonly_fields = ("audio_url", "cloudinary_id", "file_size_mb")
    fieldsets = (
        (None, {"fields": ("series", "title", "slug", "speaker", "date", "notes", "is_published")}),
        ("Video", {"fields": ("video_url",)}),
        (
            "Audio (Cloudinary)",
            {
                "fields": ("audio_file_upload", "audio_url", "cloudinary_id", "file_size_mb", "thumbnail_url"),
                "description": "Upload a raw MP3 below — it's compressed to 64kbps and uploaded to "
                               "Cloudinary automatically. audio_url / cloudinary_id / file_size_mb are "
                               "set for you; they aren't meant to be edited by hand.",
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        class FormWithUpload(form):
            audio_file_upload = SermonAudioUploadForm.base_fields["audio_file"]

        return FormWithUpload

    def save_model(self, request, obj, form, change):
        # By this point form.is_valid() has already mutated obj's in-memory
        # fields (video_url, etc.) via construct_instance — obj no longer
        # reflects what's in the DB. Query separately for the true pre-edit
        # state so "did this sermon just become complete" is measured
        # correctly.
        if change:
            original = Sermon.objects.filter(pk=obj.pk).first()
            had_content = bool(original.audio_url) or bool(original.video_url) if original else False
        else:
            had_content = False

        uploaded_file = form.cleaned_data.get("audio_file_upload")
        uploaded_something = False

        if uploaded_file:
            upload_form = SermonAudioUploadForm(files={"audio_file": uploaded_file})
            if upload_form.is_valid():
                result = upload_form.process_and_upload()
                if result:
                    obj.audio_url, obj.cloudinary_id, obj.file_size_mb = result
                    uploaded_something = True

        super().save_model(request, obj, form, change)

        if uploaded_something:
            messages.success(request, f"Audio uploaded to Cloudinary ({obj.file_size_mb} MB).")

        has_content_now = bool(obj.audio_url) or bool(obj.video_url)
        if not had_content and has_content_now and obj.is_published:
            from newsletter.services import notify_new_sermon
            notify_new_sermon(obj, request=request)
            if uploaded_something:
                from core.push import send_push_to_all_devices
                send_push_to_all_devices(
                    title="New Sermon",
                    body=f"{obj.title} is now available",
                    data={"type": "sermon", "sermon_id": str(obj.pk)},
                )
