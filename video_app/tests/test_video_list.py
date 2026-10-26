from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from video_app.models import Genre, Video



class VideoListTest(APITestCase):
    """Tests for the video list endpoint."""

    def test_returns_unauthorized_without_access_token(self):
        """Reject request without access token."""

        response = self.client.get(
            "/api/video/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_returns_videos_with_genres(self):
        """Test that returned videos has genres."""

        user = get_user_model().objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )
        access_token = RefreshToken.for_user(user).access_token
        self.client.cookies["access_token"] = str(access_token)

        genre = Genre.objects.create(name="Drama")
        video = Video.objects.create(
            title="Testvideo",
            original_file="originals/test.mp4",
        )
        video.genres.add(genre)

        response = self.client.get(
            "/api/video/",
            HTTP_HOST="localhost",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "Testvideo",
        )
        self.assertEqual(
            response.data[0]["genres"][0]["name"],
            "Drama",
        )
