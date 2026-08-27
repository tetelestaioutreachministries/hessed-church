from django import forms

from devotionals.models import Devotional
from events.models import Event
from groups.models import ConnectGroup
from sermons.models import Series, Sermon
from volunteer.models import Department

_INPUT = "h-full-width h-remove-bottom"


class DevotionalForm(forms.ModelForm):
    class Meta:
        model = Devotional
        fields = ["date", "title", "verse", "content","is_published"]
        widgets = {
            "date": forms.DateInput(attrs={"class": _INPUT, "type": "date"}),
            "title": forms.TextInput(attrs={"class": _INPUT}),
            "verse": forms.TextInput(attrs={"class": _INPUT, "placeholder": "e.g. Psalm 23:1"}),
            "content": forms.Textarea(attrs={"class": _INPUT, "rows": 8}),
        }


class SermonManageForm(forms.ModelForm):
    """Same idea as the admin's SermonAudioUploadForm, but surfaced on a
    plain staff-facing page instead of /admin/. audio_file is a plain
    upload field, not a model field — the view compresses + uploads it to
    Cloudinary and fills in audio_url/cloudinary_id/file_size_mb."""

    audio_file = forms.FileField(
        required=False,
        help_text="Upload an MP3 — it's compressed to 64kbps and uploaded to Cloudinary automatically.",
    )

    class Meta:
        model = Sermon
        fields = ["series", "title", "speaker", "date", "video_url", "notes","is_published"]
        widgets = {
            "series": forms.Select(attrs={"class": _INPUT}),
            "title": forms.TextInput(attrs={"class": _INPUT}),
            "speaker": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Speaker name"}),
            "date": forms.DateInput(attrs={"class": _INPUT, "type": "date"}),
            "video_url": forms.URLInput(attrs={"class": _INPUT, "placeholder": "https://..."}),
            "notes": forms.Textarea(attrs={"class": _INPUT, "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["series"].queryset = Series.objects.all().order_by("-created_at")
        self.fields["video_url"].required = False
        self.fields["notes"].required = False


class EventManageForm(forms.ModelForm):
    """Same idea for events — poster_file is a plain upload field handled
    by the view (resize/compress/upload to Cloudinary -> poster_url/cloudinary_id)."""

    poster_file = forms.ImageField(
        required=False,
        help_text="Upload a poster JPG — it's resized (max 1080x1920) and compressed under 300KB automatically.",
    )

    class Meta:
        model = Event
        fields = [
            "title", "summary", "description", "image",
            "date", "start_time", "end_time", "location", "age_group", "cost", "is_published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": _INPUT}),
            "summary": forms.Textarea(attrs={"class": _INPUT, "rows": 3}),
            "description": forms.Textarea(attrs={"class": _INPUT, "rows": 6}),
            "date": forms.DateInput(attrs={"class": _INPUT, "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": _INPUT, "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": _INPUT, "type": "time"}),
            "location": forms.TextInput(attrs={"class": _INPUT}),
            "age_group": forms.TextInput(attrs={"class": _INPUT, "placeholder": "e.g. 7-12 Years Old"}),
            "cost": forms.TextInput(attrs={"class": _INPUT, "placeholder": "e.g. Free"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("description", "location", "age_group", "cost", "start_time", "end_time", "image"):
            self.fields[name].required = False


class ConnectGroupManageForm(forms.ModelForm):
    class Meta:
        model = ConnectGroup
        fields = ["name", "leader_name", "leader_email", "meeting_day", "meeting_time", "location", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT}),
            "leader_name": forms.TextInput(attrs={"class": _INPUT}),
            "leader_email": forms.EmailInput(attrs={"class": _INPUT}),
            "meeting_day": forms.TextInput(attrs={"class": _INPUT}),
            "meeting_time": forms.TextInput(attrs={"class": _INPUT}),
            "location": forms.TextInput(attrs={"class": _INPUT}),
            "description": forms.Textarea(attrs={"class": _INPUT, "rows": 3}),
        }


class DepartmentManageForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description", "contact_name", "contact_email", "order", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": _INPUT}),
            "description": forms.Textarea(attrs={"class": _INPUT, "rows": 3}),
            "contact_name": forms.TextInput(attrs={"class": _INPUT}),
            "contact_email": forms.EmailInput(attrs={"class": _INPUT}),
            "order": forms.NumberInput(attrs={"class": _INPUT}),
        }
