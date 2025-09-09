from rest_framework import viewsets, mixins, permissions

from borrowings_service.models import Borrowing
from borrowings_service.serializers import BorrowingSerializer


class BorrowingsListRetrieveAPIView(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (permissions.IsAuthenticated,)
