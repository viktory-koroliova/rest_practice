from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):

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
