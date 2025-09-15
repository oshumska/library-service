import requests
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from library_service.settings import (
    TELEGRAM_API_URL,
    BASE_CHAT_ID,
    NGROK_URL,
)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def setwebhook(request):
    response = requests.post(TELEGRAM_API_URL + "setWebhook?url=" + NGROK_URL).json()
    return Response(response, status=status.HTTP_200_OK)


def send_message_to_chat(message: str):
    payload = {
        "chat_id": BASE_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    requests.post(TELEGRAM_API_URL + "sendMessage", data=payload)


def send_private_message(message: str, chat_id: int):
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    requests.post(TELEGRAM_API_URL + "sendMessage", data=payload)
