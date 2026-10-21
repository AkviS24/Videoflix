from django.db import models


class Genre(models.Model):
    """Response a genre that can be assigned to multiple videos."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Video(models.Model):
    """Stores a video`s metadata and original media file."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(
        Genre,
        related_name="videos",
        blank=True,
    )
    original_file = models.FileField(upload_to="originals/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
