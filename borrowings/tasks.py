import asyncio

from borrowings.models import Borrowing
from datetime import timedelta, date
from celery import shared_task

from borrowings.telegram_notifications import send_telegram_notification


@shared_task
def check_overdue_borrowings():
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=date.today() + timedelta(days=1)
    ).filter(actual_return_date=None)
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            asyncio.run(send_telegram_notification(
                f"Borrowing of {borrowing.book} is overdue by user {borrowing.user}."
            ))
    else:
        asyncio.run(send_telegram_notification(
            "No borrowings overdue today!"
        ))
