from rest_framework.generics import ListAPIView

from video_app.models import Video
from .serializers import VideoSerializer



class VideoListView(ListAPIView):
    """Return videos for the dashboard."""

    queryset = Video.objects.prefetch_related("genres").all()
    serializer_class = VideoSerializer
