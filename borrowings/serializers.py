from typing import Any

from django.core.exceptions import ValidationError
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

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


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.StringRelatedField(many=False, read_only=True)


class BorrowingCreateSerializer(serializers.ModelSerializer):
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
        book_to_update = Book.objects.get(title=validated_data["book"])
        if not book_to_update.inventory:
            raise ValidationError("This book is currently out of stock")
        book_to_update.inventory -= 1
        book_to_update.save()
        return super().create(validated_data)
