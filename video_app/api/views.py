from django.http import FileResponse

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from video_app.functions import get_hls_file
from video_app.models import Video
from .serializers import VideoSerializer



class VideoListView(ListAPIView):
    """Return videos for the dashboard."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]



class HLSPlaylistView(APIView):
    """Return an HLS playlist for a video and resolution."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Return the requested HLS playlist."""

        file_path = get_hls_file(movie_id, resolution, "index.m3u8")
        return FileResponse(
            file_path.open("rb"),
            content_type="application/vnd.apple.mpegurl",
        )



class HLSSegmentView(APIView):
    """Return an HLS video segment."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Return the requested HLS video segment."""

        file_path = get_hls_file(movie_id, resolution, segment)
        return FileResponse(
            file_path.open("rb"),
            content_type="video/MP2T",
        )
