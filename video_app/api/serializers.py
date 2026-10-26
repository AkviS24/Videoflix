from rest_framework import serializers

from ..models import Video



class VideoSerializer(serializers.ModelSerializer):
    """Serializes video metadata for the video API"""

    thumbnail_url = serializers.FileField(
        source="thumbnail",
        read_only=True,
    )

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]
