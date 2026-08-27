from django import forms

from core.media_processing import compress_image_under_300kb, upload_to_cloudinary


class EventPosterUploadForm(forms.Form):
    """Rendered as an extra field on the Event admin change form (see
    events/admin.py). Accepts a raw poster JPG, resizes to at most
    1080x1920 and compresses under 300KB, uploads to Cloudinary, and hands
    back the result so the admin can populate poster_url / cloudinary_id."""

    poster_file = forms.ImageField(
        required=False,
        help_text="Upload a poster JPG. It will be resized (max 1080x1920) and compressed under 300KB automatically.",
    )

    def process_and_upload(self):
        """Returns (secure_url, public_id) or None if no file was submitted."""
        uploaded = self.cleaned_data.get("poster_file")
        if not uploaded:
            return None

        compressed_path = compress_image_under_300kb(uploaded)
        result = upload_to_cloudinary(compressed_path, folder="posters")
        return result["secure_url"], result["public_id"]
