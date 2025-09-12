import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books_service.models import Book
from borrowings_service.models import Borrowing
from books_service.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class CreateBorrowingSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(CreateBorrowingSerializer, self).validate(attrs=attrs)
        expected_return_date = attrs.get(
            "expected_return_date", getattr(self.instance, "expected_return_date", None)
        )
        Borrowing.validate_borrowing(expected_return_date, ValidationError)
        book = attrs.get("book", None)
        if book.inventory <= 0:
            raise ValidationError(
                "insufficient inventory, inventory must be greater than 0"
            )

        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.get("book")
            book.inventory -= 1
            book.save()
            return Borrowing.objects.create(**validated_data)

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")


class ReturnBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id",)

    def update(self, instance, validated_data):
        borrowing = super().update(instance, validated_data)
        if not borrowing.actual_return_date:
            borrowing.actual_return_date = datetime.date.today()
            borrowing.save()
            borrowing.book.inventory += 1
            borrowing.book.save()
            return borrowing
        raise ValidationError("already returned")
