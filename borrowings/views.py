import datetime
from typing import Type, Optional

from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self) -> QuerySet:
        queryset = Borrowing.objects.all().select_related("book")

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        if is_active:
            queryset = queryset.filter(actual_return_date=None)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        if self.request.user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer: Type[Serializer]) -> None:
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated]
    )
    def return_book(
            self,
            request: Request,
            pk: Optional[int] = None
    ) -> Response:

        """Endpoint for borrowing returning"""
        borrowing = self.get_object()
        book = borrowing.book
        serializer = self.get_serializer(borrowing, data=request.data)

        if serializer.is_valid():
            book.inventory += 1
            book.save()
            borrowing.actual_return_date = datetime.date.today()
            serializer.save()

            return Response(
                {"status": "Your book was successfully returned",
                 },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
