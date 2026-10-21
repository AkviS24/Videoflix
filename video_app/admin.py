from django.contrib import admin

from .models import Genre, Video



@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Configure genre management in Django admin."""

    search_fields = ["name"]



@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configures video management in Django admin."""

    list_display = ["title", "created_at"]
    list_filter = ["genres", "created_at"]
    search_fields = ["title", "description"]
    filter_horizontal = ["genres"]
