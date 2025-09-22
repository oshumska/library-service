import stripe
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment_service.models import Payment
from payment_service.serializers import PaymentListSerializer, PaymentDetailSerializer
from library_service.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            return queryset
        else:
            return queryset.filter(borrowing__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentListSerializer


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
