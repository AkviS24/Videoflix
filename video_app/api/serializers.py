from rest_framework import serializers

from ..models import Genre, Video



class GenreSerializer(serializers.ModelSerializer):
    """Serializes genre data for the video API."""

    class Meta:
        model = Genre
        fields = ["id", "name"]



class VideoSerializer(serializers.ModelSerializer):
    """Serializes video metadata for the video API"""

    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "genres",
            "original_file",
            "created_at",
        ]
