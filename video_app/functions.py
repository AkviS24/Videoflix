from django.conf import settings
from django.http import Http404


def get_hls_file(video_id, resolution, filename):
    """Return an existing HLS File or raise a 404-error."""

    if resolution not in ("480p", "720p", "1080p"):
        raise Http404

    is_playlist = filename == "index.m3u8"
    is_segment = (
        filename.startswith("segment_")
        and filename.endswith(".ts")
        and len(filename[8:-3]) == 3
        and filename[8:-3].isdigit()
    )
    if not (is_playlist or is_segment):
        raise Http404

    file_path = (
        settings.MEDIA_ROOT / "hls" / str(video_id) / resolution / filename
    )
    if not file_path.is_file():
        raise Http404
    return file_path
