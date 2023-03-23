from typing import Type

from rest_framework import viewsets
from rest_framework.serializers import Serializer

from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.serializers import BorrowingDetailSerializer, BorrowingListSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related("book")
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        return BorrowingDetailSerializer

    def perform_create(self, serializer: Type[Serializer]) -> None:
        serializer.save(user=self.request.user)
