from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from video_app.models import Video
from .serializers import VideoSerializer



class VideoListView(ListAPIView):
    """Return videos for the dashboard."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
