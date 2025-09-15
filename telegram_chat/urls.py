from django.urls import path

from telegram_chat.views import setwebhook, telegram_bot

urlpatterns = [
    path("setwebhook/", setwebhook, name="set_webhook"),
    path("getpost/", telegram_bot, name="telegram_bot"),
]

app_name = "telegram-chat"
