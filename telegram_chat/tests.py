import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from telegram import Update

from library_service.settings import BASE_CHAT_ID
from telegram_chat.bot import application
from telegram_chat.views import send_message_to_chat, send_private_message

GETPOST_URL = reverse("telegram-chat:telegram_bot")
TELEGRAM_LINK_URL = reverse("telegram-chat:telegram_links")


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

    @patch("telegram_chat.views.application.process_update")
    @patch("telegram_chat.views.application.initialize")
    def test_telegram_webhook_post(self, mock_initialize, mock_process_update):
        expected_update = Update.de_json(self.mock_update, application.bot)
        mock_process_update.return_value = expected_update
        res = self.client.post(
            GETPOST_URL,
            data=json.dumps(self.mock_update),
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})
        mock_process_update.assert_awaited_once_with(expected_update)
        mock_initialize.assert_awaited()

    def test_telegram_webhook_get(self):

        res = self.client.get(GETPOST_URL)
        self.assertEqual(res.status_code, 400)


class TestSendMessages(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_send_message_to_public_chat(self):
        """test function actualy send message to public chat"""
        res = send_message_to_chat("hi from public message")
        self.assertEqual(res.status_code, 200)

    def test_send_message_to_private_chat(self):
        """test function actualy send message to private chat"""
        res = send_private_message("hi from private message", BASE_CHAT_ID)
        self.assertEqual(res.status_code, 200)


class TestTelegramLinkPublic(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TELEGRAM_LINK_URL)
        self.assertEqual(res.status_code, 401)


class TestTelegramLinkPrivate(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test@test.com", password="<PASSWORD>"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_telegram_link(self):
        res = self.client.get(TELEGRAM_LINK_URL)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Library public chat link", res.data)
        self.assertIn("Bot link", res.data)
        self.assertIn(
            "Send command to private chat with bot to get  personal notification",
            res.data,
        )
