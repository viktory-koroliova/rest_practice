from typing import Type

from rest_framework import viewsets
from rest_framework.serializers import Serializer

from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related("book")

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        if is_active:
            queryset = queryset.filter(actual_return_date=None)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        if self.request.user.is_staff and user_id:
            queryset = queryset.filter(user__id=int(user_id))
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

    def perform_create(self, serializer: Type[Serializer]) -> None:
        serializer.save(user=self.request.user)
