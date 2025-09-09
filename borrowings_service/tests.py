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
            borrow_date=datetime.date(2025, 9, 9),
            expected_return_date=datetime.date(2025, 10, 10),
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
            borrow_date=datetime.date(2025, 9, 9),
            expected_return_date=datetime.date(2025, 10, 10),
            book=self.book,
            user=self.user,
        )

    def test_list_borrowings(self):
        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_borrowing(self):
        url = detail_url(self.borrowing.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
