from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions

from payment_service.models import Payment
from payment_service.serializers import PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.ModelViewSet
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
