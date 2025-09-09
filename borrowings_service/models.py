from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="book_borrowings"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user_borrowings"
    )

    @staticmethod
    def validate_borrowing(
        borrow_date, return_date, error_to_raise, actual_return_date=None
    ):
        if not (borrow_date and return_date and borrow_date < return_date):
            raise error_to_raise("borrow date must be before return date")
        if actual_return_date and actual_return_date < borrow_date:
            raise error_to_raise("actual return date must be before borrow date")

    def clean(self):
        self.validate_borrowing(
            self.borrow_date,
            self.expected_return_date,
            ValidationError,
            self.actual_return_date,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"From: {self.borrow_date} to {self.expected_return_date}"

    class Meta:
        ordering = ["actual_return_date", "-expected_return_date"]
