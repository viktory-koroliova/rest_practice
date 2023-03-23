from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminUserOrReadOnly
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = BookSerializer
