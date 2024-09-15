"""Default setup django polls apps using PollsConfig."""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Polls app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "polls"
