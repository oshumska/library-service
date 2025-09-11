from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from books_service.models import Book
from books_service.serializers import BookSerializer
from books_service.permissions import IsAdminOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="filtering by title (ex. ?title=name)",
                required=False,
            ),
            OpenApiParameter(
                "author",
                type=OpenApiTypes.STR,
                description="filtering by author (ex. ?author=author)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Gets list of Books"""
        return super().list(request, *args, **kwargs)
