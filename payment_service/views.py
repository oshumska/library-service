import stripe
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment_service.models import Payment
from borrowings_service.models import Borrowing
from payment_service.serializers import PaymentSerializer
from library_service.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            return queryset
        else:
            return queryset.filter(borrowing__user=self.request.user)


class CreateStripeSessionView(
    APIView,
):
    def post(self, request):
        try:
            session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "USD",
                            "product_data": {"name": "book"},
                            "unit_amount": 120,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="http://127.0.0.1:8000/api/library/payment/success/",
                cancel_url="http://127.0.0.1:8000/api/library/payment/cancel/",
            )
            payload = {
                "session_id": session.id,
                "session_url": session.url,
            }
            return Response(payload, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def helper(borrowing: Borrowing) -> None:
    try:
        product_name = f"Borrowed: {borrowing.book.title}"
        duration_of_borrowing = borrowing.expected_return_date - borrowing.borrow_date
        daily_fee = borrowing.book.daily_fee
        amount = 100 * duration_of_borrowing.days * daily_fee
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "USD",
                        "product_data": {"name": product_name},
                        "unit_amount": int(amount),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/api/library/payment/success/",
            cancel_url="http://127.0.0.1:8000/api/library/payment/cancel/",
        )
        Payment.objects.create(
            type="PAYMENT",
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=amount / 100,
        )
    except Exception as e:
        raise e
