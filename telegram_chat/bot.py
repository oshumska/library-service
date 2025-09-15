from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
)

from library_service.settings import TELEGRAM_BOT_TOKEN, signer
from telegram_chat.models import TelegramUser


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update["message"]["chat"]["id"]

    if context.args:
        try:
            signed_id = context.args[0]
            user_id = int(signer.unsign(signed_id))
            await create_or_update_telegram_user(chat_id, user_id)
            await update.message.reply_text(
                "Your account has been linked to telegram bot"
            )
        except Exception as e:
            await update.message.reply_text(f"Failed to link account: {e}")
            print("linking error:  ", e)
    else:
        domain = "http://127.0.0.1:8000"
        url = reverse("users-service:register")
        await update.message.reply_text(
            f"Welcome to library if you want check our service use link: {domain}{url}"
        )


@sync_to_async
def create_or_update_telegram_user(chat_id: int, user_id: int):
    user = get_user_model().objects.get(id=user_id)
    return TelegramUser.objects.update_or_create(
        chat_id=chat_id, defaults={"user": user}
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("you said: " + update.message.text)


application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
