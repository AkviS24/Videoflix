from unittest.mock import patch

from django.test import TestCase

from video_app.models import Video



class VideoSignalTest(TestCase):
    """Tests for queueing video processing."""

    @patch("video_app.signals.django_rq.get_queue")
    def test_new_video_queues_processing(self, mock_get_queue):
        """Queue processing when a new video is created."""

        mock_queue = mock_get_queue.return_value

        with self.captureOnCommitCallbacks(execute=True):
            video = Video.objects.create(
                title="Testvideo",
                category="Drama",
                original_file="originals/test.mp4",
            )
        mock_get_queue.assert_called_once_with("default")
        mock_queue.enqueue.assert_called_once_with(
            "video_app.tasks.process_video",
            video.pk
        )
