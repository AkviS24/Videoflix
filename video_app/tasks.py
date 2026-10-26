import subprocess
from pathlib import Path

from django.conf import settings

from .models import Video


RESOLUTIONS = (480, 720, 1080)


def run_ffmpeg(command):
    """Execute an FFmpeg command and report processing failures."""

    subprocess.run(command, check=True, capture_output=True, text=True)


def create_thumbnail(video, source_path):
    """Generate and save a thumbnail for the video."""

    thumbnail_path = settings.MEDIA_ROOT / "thumbnails" / f"video_{video.pk}.jpg"
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg([
        "ffmpeg", "-y", "-ss", "00:00:01", "-i", str(source_path),
        "-frames:v", "1", "-q:v", "2", str(thumbnail_path),
    ])
    video.thumbnail.name = str(thumbnail_path.relative_to(settings.MEDIA_ROOT))
    video.save(update_fields=["thumbnail"])


def create_hls_variant(source_path, output_dir, height):
    """Create an HLS playlist and transport stream segments."""

    output_dir.mkdir(parents=True, exist_ok=True)
    run_ffmpeg([
        "ffmpeg", "-y", "-i", str(source_path),
        "-vf", f"^scale=-2:{height}", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "hls", "-hls_time", "6",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(output_dir / "segment_%03d.ts"),
        str(output_dir / "index.m3u8"),
    ])


def process_video(video_id):
    """Generate a thumbnail and HLS variants for a video."""

    video = Video.objects.get(pk=video_id)
    source_path = Path(video.original_file.path)
    if not source_path.is_file():
        raise FileNotFoundError(
            f"Original video file not found: {source_path}"
        )
    create_thumbnail(video, source_path)
    for height in RESOLUTIONS:
        output_dir = settings.MEDIA_ROOT / "hls" / str(video.pk) / f"{height}p"
        create_hls_variant(source_path, output_dir, height)
