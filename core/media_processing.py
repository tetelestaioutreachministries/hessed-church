"""
Shared helpers for compressing and uploading media to Cloudinary.

Design (per spec):
- Never store the raw upload in Postgres or keep it on local disk long-term —
  only the Cloudinary secure_url + public_id are saved to the model.
- Compress *before* uploading, to respect the Cloudinary free tier
  (25GB storage / 25GB bandwidth / 100MB max per file):
    * MP3 -> 64kbps via pydub (needs ffmpeg on the server)
    * JPG -> resized to max 1080x1920, compressed with Pillow until <300KB
"""

import io
import os
import tempfile

import cloudinary
import cloudinary.uploader
from django.conf import settings

_CONFIGURED = False


def ensure_cloudinary_configured():
    global _CONFIGURED
    if _CONFIGURED:
        return
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _CONFIGURED = True


def compress_audio_to_64kbps(uploaded_file):
    """Takes a Django UploadedFile (MP3), returns (temp_path, size_mb)."""
    from pydub import AudioSegment  # imported lazily so the whole project doesn't hard-depend on ffmpeg at import time

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as src_tmp:
        for chunk in uploaded_file.chunks():
            src_tmp.write(chunk)
        src_path = src_tmp.name

    audio = AudioSegment.from_file(src_path)
    out_path = src_path.replace(".mp3", "-64k.mp3")
    audio.export(out_path, format="mp3", bitrate="64k")

    size_mb = round(os.path.getsize(out_path) / (1024 * 1024), 2)
    os.remove(src_path)
    return out_path, size_mb


def compress_image_under_300kb(uploaded_file, max_size=(1080, 1920), max_bytes=300 * 1024):
    """Takes a Django UploadedFile (JPG), returns a temp file path resized to
    at most 1080x1920 and re-compressed with decreasing JPEG quality until it
    fits under 300KB."""
    from PIL import Image

    image = Image.open(uploaded_file)
    image = image.convert("RGB")
    image.thumbnail(max_size, Image.LANCZOS)

    quality = 90
    buffer = io.BytesIO()
    while quality >= 20:
        buffer.seek(0)
        buffer.truncate()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() <= max_bytes or quality <= 20:
            break
        quality -= 10

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as out_tmp:
        out_tmp.write(buffer.getvalue())
        out_path = out_tmp.name

    return out_path


def upload_to_cloudinary(file_path, folder):
    """Uploads a local file to Cloudinary and returns the result dict
    (contains 'secure_url' and 'public_id'). Deletes the local temp file
    afterwards — nothing is kept on disk long-term."""
    ensure_cloudinary_configured()
    result = cloudinary.uploader.upload(file_path, folder=folder, resource_type="auto")
    try:
        os.remove(file_path)
    except OSError:
        pass
    return result
