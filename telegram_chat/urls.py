from django.urls import path

from telegram_chat.views import setwebhook

urlpatterns = [
    path("setwebhook/", setwebhook, name="set_webhook"),
]

app_name = "telegram-chat"
