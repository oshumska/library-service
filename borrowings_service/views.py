from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, permissions

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingSerializer,
    CreateBorrowingSerializer,
)


class BorrowingsAPIView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        is_active = self.request.query_params.get("is_active")

        if is_active == "true":
            print("active")
            queryset = queryset.filter(actual_return_date__isnull=True)
        elif is_active == "false":
            queryset = queryset.filter(actual_return_date__isnull=False)

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            return queryset.filter(user_id=user_id)
        else:
            return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBorrowingSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.STR,
                description="filter by active status "
                "(ex. ?is_active=true or ?is_active=false)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="admin user can filter by user id (ex. ?user_id=1)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Gets list of borrowings"""
        return super().list(request, *args, **kwargs)
