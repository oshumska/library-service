from django.contrib.auth import get_user_model
from django.db import models


class TelegramUser(models.Model):

    chat_id = models.BigIntegerField(unique=True)
    user = models.OneToOneField(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="telegram",
    )
