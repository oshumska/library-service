from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("users-service:register")
USER_TOKEN_URL = reverse("users-service:token_obtain_pair")
USER_ME_URL = reverse("users-service:manage-user")


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


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

    def test_user_register_bad_request(self):
        payload = {
            "email": "username",
            "password": "<PASSWORD>",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {"email": "user@gmail.com", "password": "1234"}

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exist(self):
        payload = {
            "email": "user@gmail.com",
            "password": "<PASSWORD>",
        }
        sample_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_jwt_tokens(self):
        payload = {
            "email": "user@gmail.com",
            "password": "<PASSWORD>",
        }

        sample_user(**payload)
        res = self.client.post(USER_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_create_jwt_tokens_user_not_exist(self):
        payload = {
            "email": "user@gmail.com",
            "password": "<PASSWORD>",
        }

        res = self.client.post(USER_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_jwt_tokens_no_password(self):
        payload = {
            "email": "user@gmail.com",
            "password": "1234",
        }
        sample_user(**payload)
        res = self.client.post(USER_TOKEN_URL, email=payload["email"])
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_jwt_tokens_wrong_password(self):
        payload = {
            "email": "user@gmail.com",
            "password": "<PASSWORD>",
        }
        sample_user(**payload)
        payload.update({"password": "wrong"})
        res = self.client.post(USER_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_me_unauthorized(self):
        res = self.client.get(USER_ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserServiceTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(email="user@gmail.com", password="<PASSWORD>")
        self.client.force_authenticate(user=self.user)

    def test_user_me_success(self):
        res = self.client.get(USER_ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.user.id)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["is_staff"], self.user.is_staff)

    def test_update_profile(self):
        payload = {
            "email": "new@gmail.com",
            "first_name": "Lucy",
            "last_name": "Smith",
            "password": "newpassword",
        }
        res = self.client.patch(USER_ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["first_name"], self.user.first_name)
        self.assertEqual(res.data["last_name"], self.user.last_name)
        self.assertTrue(self.user.check_password(payload["password"]))
