import django_rq
from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configures video management in Django admin."""

    list_display = ["title", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "description"]

    def save_model(self, request, obj, form, change):
        """Save videos and enqueue processing when needed."""

        super().save_model(request, obj, form, change)
        original_changed = "original_file" in form.changed_data
        thumbnail_deleted = (
            "thumbnail" in form.changed_data and not obj.thumbnail
        )
        if original_changed or thumbnail_deleted:
            django_rq.get_queue("default").enqueue(
                "video_app.tasks.process_video", obj.pk
            )
