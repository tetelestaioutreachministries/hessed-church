from rest_framework import serializers

from devotionals.models import Devotional
from events.models import Event
from sermons.models import Sermon


class DevotionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devotional
        fields = ["id", "date", "title", "verse", "content"]


class SermonSerializer(serializers.ModelSerializer):
    # Phase 1 site templates reference sermon.speaker directly, so the model
    # field itself stays named `speaker` — only the API exposes it as `preacher`.
    preacher = serializers.CharField(source="speaker")

    class Meta:
        model = Sermon
        fields = ["id", "title", "preacher", "date", "audio_url", "thumbnail_url", "file_size_mb", "video_url"]


class EventSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source="display_description")

    class Meta:
        model = Event
        fields = ["id", "title", "slug", "date", "location", "description", "poster_url"]
