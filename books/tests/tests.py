from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list")


def sample_book(**params) -> Book:
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "HARD",
        "inventory": 11,
        "daily_fee": 1.25
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id: int) -> str:
    return reverse("books:book-detail", args=[book_id])


class NotAdminBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_books(self) -> None:
        sample_book()
        response = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_not_allowed(self) -> None:
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 11,
            "daily_fee": 1.25
        }
        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_not_allowed(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        payload = {
            "title": "Testbook",
            "inventory": 15
        }
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_not_allowed(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345"
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self) -> None:
        sample_book()
        response = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_not_allowed(self) -> None:
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 11,
            "daily_fee": 1.25
        }
        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_not_allowed(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        payload = {
            "title": "Testbook",
            "inventory": 15
        }
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_not_allowed(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self) -> None:
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "HARD",
            "inventory": 11,
            "daily_fee": 1.25
        }
        response = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_update_book(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        payload = {
            "title": "Testbook",
            "inventory": 15
        }
        response = self.client.patch(url, payload)
        updated_book = Book.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(payload[key], getattr(updated_book, key))

    def test_delete_book(self) -> None:
        book = sample_book()
        url = detail_url(book.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
