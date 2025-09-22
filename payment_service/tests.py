import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from borrowings_service.tests import sample_user, sample_book, tomorrow, yesterday
from borrowings_service.models import Borrowing
from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer
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


class PrivatePaymentTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        book = sample_book()
        self.user = sample_user(
            email="user@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)
        borrowing = sample_borrowing(book, self.user)
        self.payment = helper(borrowing)

    def test_list_payments(self):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)

        res = self.client.get(PAYMENT_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_user_see_only_own_payments(self):
        res = self.client.get(PAYMENT_LIST_URL)
        self.assertEqual(res.data["count"], 1)
        user = sample_user(
            email="user2@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=user)
        res = self.client.get(PAYMENT_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 0)

    def test_detail_payment(self):
        url = detail_url(self.payment.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AdminPaymentTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()
        self.admin = sample_user(
            email="admin@gmail.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.user = sample_user(
            email="user@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.admin)
        borrowing = sample_borrowing(self.book, self.user)
        self.payment = helper(borrowing)

    def test_admin_see_all_payments(self):
        res = self.client.get(PAYMENT_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_admin_unable_create_payment(self):
        res = self.client.post(PAYMENT_LIST_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_admin_unable_update_payment(self):
        borrowing = sample_borrowing(self.book, self.admin)
        payment = helper(borrowing)
        url = detail_url(payment.id)
        res = self.client.put(url, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
