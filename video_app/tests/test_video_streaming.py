from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase

from video_app.models import Video



class HLSPlaylistTest(APITestCase):
    """Test access to HLS playlist."""

    def test_playlist_requires_authentication(self):
        """Rejects requests without a valid access-token."""

        url = reverse(
            "video-playlist",
            kwargs={"movie_id": 1, "resolution": "720p"},
        )
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_playlist_return_file_for_authenticated_user(self):
        """Return a existing playlist for authenticated users."""

        user = get_user_model(). objects.create_user(
            username="streamuser",
            password="TestPassword123!",
        )
        self.client.cookies["access_token"] = str(
            RefreshToken.for_user(user).access_token
        )
        video = Video.objects.create(
            title="Testvideo",
            original_file="originals/test.mp4",
        )
        with TemporaryDirectory() as temp_dir:
            with override_settings(MEDIA_ROOT=Path(temp_dir)):
                playlist = (
                    Path(temp_dir) / "hls" / str(video.id) / "720p" / "index.m3u8"
                )
                playlist.parent.mkdir(parents=True)
                playlist.write_text("#EXTM3U\n", encoding="utf-8")
                url = reverse(
                    "video-playlist",
                    kwargs={"movie_id": video.id, "resolution": "720p"},
                )
                response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.apple.mpegurl",
        )
        self.assertIn(b"#EXTM3U", b"".join(response.streaming_content))



class HLSSegmentTests(APITestCase):
    """Test access to HLS video segments."""

    def test_segment_requires_authentication(self):
        """Rejects request without a valid access-token."""

        url = reverse(
            "video-segment",
            kwargs={"movie_id": 1, "resolution": "720p", "segment": "segment_000.ts"},
        )
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_segment_returns_file_for_authenticated_user(self):
        """Return a existing video segment to authenticated user."""

        user = get_user_model().objects.create_user(
            username="segmentuser",
            password="TestPassword123!",
        )
        self.client.cookies["access_token"] = str(
            RefreshToken.for_user(user).access_token
        )
        video = Video.objects.create(
            title="Testvideo",
            original_file="originals/test.mp4",
        )
        with TemporaryDirectory() as temp_dir:
            with override_settings(MEDIA_ROOT=Path(temp_dir)):
                segment = (
                    Path(temp_dir) / "hls" / str(video.id) / "720p" / "segment_000.ts"
                )
                segment.parent.mkdir(parents=True)
                segment.write_bytes(b"test-segment")
                url = reverse(
                    "video-segment",
                    kwargs={
                        "movie_id": video.id,
                        "resolution": "720p",
                        "segment": "segment_000.ts",
                    },
                )
                response = self.client.get(url)
                content = b"".join(response.streaming_content)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            "video/MP2T",
        )
        self.assertEqual(
            content,
            b"test-segment",
        )

    def test_segment_returns_404_when_file_is_missing(self):
        """Return 404 if the requested video-segment does not exist."""

        user = get_user_model().objects.create_user(
            username="missingsegmentuser",
            password="TestPassword123!",
        )
        self.client.cookies["access_token"] = str(
            RefreshToken.for_user(user).access_token
        )
        video = Video.objects.create(
            title="Testvideo",
            original_file="originals/test.mp4",
        )
        with TemporaryDirectory() as temp_dir:
            with override_settings(MEDIA_ROOT=Path(temp_dir)):
                url = reverse(
                    "video-segment",
                    kwargs={
                        "movie_id": video.id,
                        "resolution": "720p",
                        "segment": "segment_000.ts",
                    },
                )
                response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
