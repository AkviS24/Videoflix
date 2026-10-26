from django.contrib import admin

from .models import Video



@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configures video management in Django admin."""

    list_display = ["title", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "description"]
