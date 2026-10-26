from django.db import models



class Video(models.Model):
    """Stores a video`s metadata and original media file."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    original_file = models.FileField(upload_to="originals/")
    thumbnail = models.FileField(
        upload_to="thumbnails/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
