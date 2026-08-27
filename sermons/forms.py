from django import forms

from core.media_processing import compress_audio_to_64kbps, upload_to_cloudinary


class SermonAudioUploadForm(forms.Form):
    """Rendered as an extra field on the Sermon admin change form (see
    sermons/admin.py). Not a model field — its only job is to accept a raw
    MP3, compress it, upload it to Cloudinary, and hand back the result so
    the admin can populate audio_url / cloudinary_id / file_size_mb."""

    audio_file = forms.FileField(
        required=False,
        help_text="Upload an MP3. It will be compressed to 64kbps and uploaded to Cloudinary automatically.",
    )

    def process_and_upload(self):
        """Returns (secure_url, public_id, file_size_mb) or None if no file was submitted."""
        uploaded = self.cleaned_data.get("audio_file")
        if not uploaded:
            return None

        compressed_path, size_mb = compress_audio_to_64kbps(uploaded)
        result = upload_to_cloudinary(compressed_path, folder="sermons")
        return result["secure_url"], result["public_id"], size_mb
