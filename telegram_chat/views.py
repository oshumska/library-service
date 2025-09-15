import requests

from library_service.settings import TELEGRAM_API_URL, BASE_CHAT_ID


def send_message_to_chat(message: str):
    payload = {
        "chat_id": BASE_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    requests.post(TELEGRAM_API_URL + "sendMessage", data=payload)
