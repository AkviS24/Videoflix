import subprocess

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from django.test import TestCase, override_settings

from video_app.models import Video
from video_app.tasks import (
    create_hls_variant,
    create_thumbnail,
    process_video,
    run_ffmpeg,
)


class ProcessVideoTest(TestCase):
    """Test video processing tasks."""

    @patch("video_app.tasks.create_thumbnail")
    def test_process_video_raises_error_when_source_is_missing(
        self, mock_create_thumbnail
    ):
        """Raise an error if the original video file is missing."""

        video = Video.objects.create(
            title="Testvideo",
            category="Drama",
            original_file="originals/missing.mp4",
        )

        with self.assertRaises(FileNotFoundError):
            process_video(video.pk)

        mock_create_thumbnail.assert_not_called()

    @patch("video_app.tasks.create_hls_variant")
    @patch("video_app.tasks.create_thumbnail")
    def test_process_video_creates_thumbnail_and_hls_variants(
        self, mock_create_thumbnail, mock_create_hls_variant
    ):
        """Create a thumbnail and HLS-variants for all resolutions."""

        with TemporaryDirectory() as temp_dir:
            media_root = Path(temp_dir)
            source_path = media_root / "originals" / "source.mp4"
            source_path.parent.mkdir(parents=True)
            source_path.write_bytes(b"fake video")

            with override_settings(MEDIA_ROOT=media_root):
                video = Video.objects.create(
                    title="Testvideo",
                    category="Drama",
                    original_file="originals/source.mp4",
                )
                process_video(video.pk)

            mock_create_thumbnail.assert_called_once_with(video, source_path)
            self.assertEqual(mock_create_hls_variant.call_count, 3)
            self.assertEqual(
                [entry.args[2] for entry in mock_create_hls_variant.call_args_list],
                [480, 720, 1080],
            )

    @patch("video_app.tasks.subprocess.run")
    def test_run_ffmpeg_raises_error_when_command_fail(self, mock_run):
        """Raise an error when FFmpeg execution fails."""

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["ffmpeg"]
        )

        with self.assertRaises(subprocess.CalledProcessError):
            run_ffmpeg(["ffmpeg", "-version"])

        mock_run.assert_called_once_with(
            ["ffmpeg", "-version"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("video_app.tasks.run_ffmpeg")
    def test_create_thumbnail_saves_thumbnail_path(self, mock_run_ffmpeg):
        """Generate a thumbnail and save its relative path."""

        with TemporaryDirectory() as temp_dir:
            media_root = Path(temp_dir)
            source_path = media_root / "originals" / "source.mp4"
            video = Video.objects.create(
                title="Testvideo",
                category="Drama",
                original_file="originals/source.mp4",
            )

            with override_settings(MEDIA_ROOT=media_root):
                create_thumbnail(video, source_path)

            video.refresh_from_db()
            self.assertEqual(
                video.thumbnail.name,
                f"thumbnails/video_{video.pk}.jpg",
            )
            mock_run_ffmpeg.assert_called_once()

    @patch("video_app.tasks.run_ffmpeg")
    def test_create_hls_variant_builds_ffmpeg_command(self, mock_run_ffmpeg):
        """Build the FFmpeg Command for HLS-variant."""

        with TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "source.mp4"
            output_dir = Path(temp_dir) / "720p"

            create_hls_variant(source_path, output_dir, 720)

            command = mock_run_ffmpeg.call_args.args[0]
            self.assertIn("scale=-2:720", command)
            self.assertIn("hls", command)
            self.assertIn(str(output_dir / "index.m3u8"), command)
            self.assertTrue(output_dir.is_dir())
