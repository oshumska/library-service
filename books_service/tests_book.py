from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from decimal import Decimal, ROUND_HALF_UP

from rest_framework.test import APIClient

from books_service.models import Book
from books_service.serializers import BookSerializer

BOOK_LIST_URL = reverse("books-service:book-list")


def detail_url(book_id):
    return reverse("books-service:book-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Tiffany Smith",
        "cover": "HARD",
        "inventory": 20,
        "daily_fee": 0.5,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class PublicBookAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()

    def test_list_book(self):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        res = self.client.get(BOOK_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "New Book",
            "author": "Tiffany Smith",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 1,
        }
        res = self.client.post(BOOK_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_book(self):
        url = detail_url(self.book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], self.book.title)
        self.assertEqual(res.data["author"], self.book.author)
        self.assertEqual(res.data["cover"], self.book.cover)
        self.assertEqual(res.data["inventory"], self.book.inventory)
        daily_fee = str(
            Decimal(str(self.book.daily_fee)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )
        self.assertEqual(res.data["daily_fee"], daily_fee)

    def test_update_book_forbidden(self):
        url = detail_url(self.book.id)
        payload = {
            "title": "New Book",
            "author": "Tiffany Smith",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 1,
        }
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_forbidden(self):
        url = detail_url(self.book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@ gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        payload = {
            "title": "New Book",
            "author": "Tiffany Smith",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 1,
        }
        res = self.client.post(BOOK_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        book = sample_book()
        url = detail_url(book.id)
        payload = {
            "title": "New Book",
            "author": "Tiffany Smith",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 1,
        }
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@gmail.com",
            password="password1",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_create_book(self):
        payload = {
            "title": "New Book",
            "author": "Tiffany Smith",
            "cover": "HARD",
            "inventory": 15,
            "daily_fee": 1,
        }
        res = self.client.post(BOOK_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_book_bad_payload(self):
        payload = {
            "title": "New Book",
        }
        res = self.client.post(BOOK_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_book_unknown_cover(self):
        payload = {
            "title": "New Book",
            "author": "Tiffany Smith",
            "cover": "UNKNOWN",
            "inventory": 15,
            "daily_fee": 1,
        }
        res = self.client.post(BOOK_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_book(self):
        payload = {
            "title": "Updated Book",
            "author": "Tiffany Smith",
            "cover": "SOFT",
            "inventory": 20,
            "daily_fee": 0.5,
        }
        daily_fee = self.book.daily_fee
        url = detail_url(self.book.id)
        res = self.client.put(url, payload)
        self.book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], self.book.title)
        self.assertEqual(res.data["cover"], payload["cover"])

    def test_delete_book(self):
        url = detail_url(self.book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
