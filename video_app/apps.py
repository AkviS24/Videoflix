from django.apps import AppConfig



class VideoAppConfig(AppConfig):
    name = 'video_app'

    def ready(self):
        """Load video_app signal handlers."""

        import video_app.signals
