from django.apps import AppConfig



class VideoAppConfig(AppConfig):
    """Configure the video application and its signal handlers."""

    name = 'video_app'

    def ready(self):
        """Load video_app signal handlers."""

        import video_app.signals
