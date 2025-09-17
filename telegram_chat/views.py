import requests
import json
import logging

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters

from library_service.settings import (
    TELEGRAM_API_URL,
    BASE_CHAT_ID,
    NGROK_URL,
    signer,
    BOT_USERNAME,
    BASE_CHAT_USERNAME,
)
from telegram_chat.bot import (
    application,
    start_command,
    text_handler,
)

logger = logging.getLogger(__name__)

if not application.handlers:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    )

application_initialized = False


@csrf_exempt
async def telegram_bot(request):
    global application_initialized
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            update = Update.de_json(data, application.bot)

            if not application_initialized:
                await application.initialize()
                application_initialized = True

            await application.process_update(update)

            return JsonResponse({"ok": True})
        except Exception as e:
            logger.exception("Webhook error")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"GET not allowed": "Bad Request"}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_telegram_link(request):
    user = request.user
    signed_id = signer.sign(str(user.id))
    invite_link = f"https://t.me/{BASE_CHAT_USERNAME}"

    url = f"https://t.me/{BOT_USERNAME}"
    command = f"/start {signed_id}"
    payload = {
        "Library public chat link": invite_link,
        "Bot link": url,
        "Send command to private chat with bot to get  personal notification": command,
    }
    return Response(data=payload, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def setwebhook(request):
    response = requests.post(
        TELEGRAM_API_URL + "setWebhook?url=" + NGROK_URL, timeout=5
    ).json()
    return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def delete_webhook(request):
    response = requests.post(TELEGRAM_API_URL + "setWebhook?url=", timeout=5).json()
    return Response(response, status=status.HTTP_200_OK)


def send_message_to_chat(message: str):
    payload = {
        "chat_id": BASE_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    requests.post(TELEGRAM_API_URL + "sendMessage", data=payload, timeout=5)


def send_private_message(message: str, chat_id: int):
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    requests.post(TELEGRAM_API_URL + "sendMessage", data=payload, timeout=5)
