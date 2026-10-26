import django_rq
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video



@receiver(post_save, sender=Video)
def queue_video_processing(sender, instance, created, **kwargs):
    """Queue processing when a new video with an original file is saved."""

    if not created or not instance.original_file:
        return

    transaction.on_commit(
        lambda: django_rq.get_queue("default").enqueue(
            "video_app.tasks.process_video",
            instance.pk,
        )
    )
