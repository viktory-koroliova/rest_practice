import asyncio
from typing import Any

from django.core.exceptions import ValidationError
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.telegram_notifications import send_telegram_notification


class BorrowingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user"
        )

    def create(self, validated_data: dict[str, Any]) -> Borrowing:
        book = Book.objects.get(title=validated_data["book"])
        if not book.inventory:
            raise ValidationError("This book is currently out of stock")
        book.inventory -= 1
        book.save()

        asyncio.run(
            send_telegram_notification(
                f"Book {book.title} was borrowed by {validated_data['user']}. "
                f"Expected return date: {validated_data['expected_return_date']}"
            )
        )

        return super().create(validated_data)


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id",)

    def validate(self, attrs):
        if self.instance.actual_return_date:
            raise ValidationError("This book is already returned")
        return attrs
