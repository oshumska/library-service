import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from borrowings_service.tests import sample_user, sample_book, tomorrow, yesterday
from borrowings_service.models import Borrowing
from payment_service.views import helper


PAYMENT_LIST_URL = reverse("payment-service:payment-list")


def detail_url(payment_id):
    return reverse("payment-service:payment-detail", args=[payment_id])


def sample_borrowing(book, user):
    return Borrowing.objects.create(
        borrow_date=yesterday(),
        expected_return_date=tomorrow() + datetime.timedelta(days=10),
        book=book,
        user=user,
    )


class PublicPaymentTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        book = sample_book()
        user = sample_user(
            email="user@gmail.com",
            password="<PASSWORD>",
        )
        borrowing = sample_borrowing(book, user)
        self.payment = helper(borrowing)

    def test_list_borrowings(self):
        res = self.client.get(PAYMENT_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_borrowing(self):
        url = detail_url(self.payment.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
