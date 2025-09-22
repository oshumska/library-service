import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowings_service.models import Borrowing
from books_service.serializers import BookSerializer
from telegram_chat.views import send_message_to_chat, send_private_message
from payment_service.views import helper
from payment_service.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payment = PaymentSerializer(source="payments", many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payment",
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
            if book.inventory == 0:
                massage = f"We out of stock of the {book.title} by {book.author}"
                send_message_to_chat(massage)
            elif book.inventory <= 3:
                message = (
                    f"Only {book.inventory} copy of {book.title} by {book.author} left"
                )
                send_message_to_chat(message)
            else:
                message = f"Have you already read {book.title} by {book.author}"
                send_message_to_chat(message)
            user = validated_data.get("user")
            if hasattr(user, "telegram"):
                return_date = validated_data.get("expected_return_date")
                message = (
                    f"Congratulations you just borrowed {book.title} by {book.author},"
                    f" make sure you finish reading by {return_date}"
                )
                send_private_message(message, chat_id=user.telegram.chat_id)
            borrowing = Borrowing.objects.create(**validated_data)
            helper(borrowing)
            return borrowing

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
