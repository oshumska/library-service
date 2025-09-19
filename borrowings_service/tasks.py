from borrowings_service.models import Borrowing
from telegram_chat.views import send_message_to_chat, send_private_message

from celery import shared_task
from django.utils.timezone import now


@shared_task
def send_message_for_overdue_borrowings():
    borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lte=now().date()
    )
    if borrowings:
        for borrowing in borrowings:
            message = f"User with id {borrowing.user.id} overdue borrowing of {borrowing.book.id} by {borrowing.book.author}"
            send_message_to_chat(message)
            if hasattr(borrowing.user, "telegram"):
                message = (
                    f"Hey, you borrowed {borrowing.book.title} at {borrowing.borrow_date}. "
                    f"Expected return date: {borrowing.expected_return_date} has "
                    f"already passed. Please return book as soon as possible"
                )
                send_private_message(message, borrowing.user.telegram.chat_id)
    else:
        send_message_to_chat("No borrowings overdue today!")
