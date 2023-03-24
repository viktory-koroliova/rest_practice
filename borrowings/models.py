from __future__ import annotations

import datetime
from typing import Optional, Type, Any

from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(to=Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="borrowings")

    class Meta:
        ordering = ["-borrow_date"]

    @staticmethod
    def validate_date(
            expected_return_date: datetime.date,
            error_to_raise: Type[ValidationError],
            actual_return_date: Optional[datetime.date] = None
    ) -> None:
        if actual_return_date:
            if not (
                    (datetime.date.today() <= expected_return_date)
                    and (expected_return_date <= actual_return_date)
            ):
                raise error_to_raise(
                    "Expected and Actual return date "
                    "cannot be earlier than today's date")
        else:
            if not (datetime.date.today() <= expected_return_date):
                raise error_to_raise(
                    "Expected return date cannot be earlier than today's date"
                )

    def clean(self) -> None:
        Borrowing.validate_date(
            self.expected_return_date,
            ValidationError,
            self.actual_return_date,
        )

    def save(
            self,
            force_insert: bool = False,
            force_update: bool = False,
            using: Optional[Any] = None,
            update_fields: Optional[Any] = None,
    ) -> Borrowing:
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return (
            f"Book {self.book.id} ordered on {self.borrow_date}, "
            f"return date - {self.expected_return_date}"
        )
