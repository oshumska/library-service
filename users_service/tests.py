from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("users-service:register")


class PublicUserServiceTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_register(self):
        payload = {
            "email": "user@gmail.com",
            "password": "<PASSWORD>",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)
