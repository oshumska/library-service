import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APIClient

from books_service.models import Book
from borrowings_service.models import Borrowing
from borrowings_service.serializers import BorrowingSerializer

BORROWING_LIST_URL = reverse("borrowings_service:borrowing-list")


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


def yesterday():
    return datetime.date.today() - datetime.timedelta(days=1)


def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


def detail_url(borrowing_id):
    return reverse("borrowings_service:borrowing-detail", args=[borrowing_id])


class PublicBorrowingTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        book = sample_book()
        user = sample_user(
            email="user@gmail.com",
            password="<PASSWORD>",
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=yesterday(),
            expected_return_date=tomorrow() + datetime.timedelta(days=10),
            book=book,
            user=user,
        )

    def test_list_borrowings(self):
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_borrowing(self):
        url = detail_url(self.borrowing.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBorrowingTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(
            email="user@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)
        self.book = sample_book()
        self.borrowing = Borrowing.objects.create(
            borrow_date=yesterday(),
            expected_return_date=tomorrow() + datetime.timedelta(days=10),
            book=self.book,
            user=self.user,
        )

    def test_list_borrowings(self):
        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_user_see_only_own_borrowings(self):
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        user = sample_user(
            email="user2@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=user)
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 0)

    def test_filter_by_is_active_borrowings(self):
        payload = {
            "is_active": "true",
        }
        res = self.client.get(BORROWING_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.borrowing.actual_return_date = tomorrow()
        self.borrowing.save()
        res = self.client.get(BORROWING_LIST_URL, payload)
        self.assertEqual(res.data["count"], 0)
        payload = {
            "is_active": "false",
        }
        res = self.client.get(BORROWING_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_detail_borrowing(self):
        url = detail_url(self.borrowing.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_borrowing(self):
        book_inventory = self.book.inventory
        payload = {
            "expected_return_date": tomorrow(),
            "book": self.book.id,
        }
        res = self.client.post(BORROWING_LIST_URL, payload)
        book_inventory -= 1
        self.book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book_inventory, self.book.inventory)

    def test_create_borrowing_with_invalid_date(self):
        payload = {
            "expected_return_date": yesterday(),
            "book": self.book.id,
        }
        res = self.client.post(BORROWING_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_with_zero_book_inventory(self):
        book = sample_book(inventory=0)
        payload = {
            "expected_return_date": tomorrow(),
            "book": book.id,
        }
        res = self.client.post(BORROWING_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AdminBorrowingTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = sample_user(
            email="admin@gmail.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin)
        self.user = sample_user(
            email="user@gmail.com",
            password="<PASSWORD>",
        )
        self.book = sample_book()
        self.borrowing = Borrowing.objects.create(
            borrow_date=yesterday(),
            expected_return_date=tomorrow() + datetime.timedelta(days=10),
            book=self.book,
            user=self.user,
        )

    def test_admin_see_all_borrowings(self):
        res = self.client.get(BORROWING_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_filter_user_by_id(self):
        Borrowing.objects.create(
            borrow_date=yesterday(),
            expected_return_date=tomorrow() + datetime.timedelta(days=10),
            book=self.book,
            user=self.admin,
        )
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.data["count"], 2)

        payload = {
            "user_id": self.user.id,
        }
        res = self.client.get(BORROWING_LIST_URL, payload)
        self.assertEqual(res.data["count"], 1)
