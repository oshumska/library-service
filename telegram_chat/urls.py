from django.urls import path

from telegram_chat.views import (
    setwebhook,
    telegram_bot,
    get_telegram_link,
    delete_webhook,
)

urlpatterns = [
    path("set/webhook/", setwebhook, name="set_webhook"),
    path("getpost/", telegram_bot, name="telegram_bot"),
    path("links/", get_telegram_link, name="telegram_links"),
    path("delete/webhook/", delete_webhook, name="delete_webhook"),
]

app_name = "telegram-chat"
