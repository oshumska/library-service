import json

from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


GETPOST_URL = reverse("telegram-chat:telegram_bot")


class TelegramWebhookTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.mock_update = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 12345678,
                    "is_bot": False,
                    "first_name": "Test",
                    "language_code": "uk",
                },
                "chat": {"id": 12345678, "first_name": "Test", "type": "private"},
                "date": 1758041111,
                "text": "Hello, bot",
            },
        }

    def test_telegram_webhook_post(self):

        res = self.client.post(
            GETPOST_URL,
            data=json.dumps(self.mock_update),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})

    def test_telegram_webhook_get(self):

        res = self.client.get(GETPOST_URL)
        self.assertEqual(res.status_code, 400)
