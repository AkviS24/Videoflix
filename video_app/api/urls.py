from django.urls import path

from .views import HLSSegmentView, HLSPlaylistView, VideoListView


urlpatterns = [
    path("", VideoListView.as_view(), name="video-list"),
    path("<int:movie_id>/<str:resolution>/index.m3u8", HLSPlaylistView.as_view(), name="video-playlist"),
    path("<int:movie_id>/<str:resolution>/<str:segment>/", HLSSegmentView.as_view(), name="video-segment"),
]
