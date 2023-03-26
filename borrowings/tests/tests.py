from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")
INVENTORY = 10


def sample_book(**params) -> Book:
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "HARD",
        "inventory": INVENTORY,
        "daily_fee": 1.25
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params) -> Borrowing:
    defaults = {
        "expected_return_date": "2023-10-10",
        "book": sample_book()
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


def detail_url(borrowing_id: int) -> str:
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345"
        )
        self.client.force_authenticate(self.user)

    def test_borrowing_list(self) -> None:
        sample_borrowing(user=self.user)
        response = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_borrowing_detail(self) -> None:
        borrowing = sample_borrowing(user=self.user)
        url = detail_url(borrowing.id)

        response = self.client.get(url)
        serializer = BorrowingListSerializer(borrowing)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_borrowing_with_valid_data(self) -> None:
        payload = {
            "borrow_date": "2023-10-10",
            "expected_return_date": "2023-10-20",
            "user": self.user.id,
            "book": sample_book().id,
        }

        response = self.client.post(BORROWING_URL, payload)
        book = Book.objects.get(pk=response.data["book"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.inventory, INVENTORY - 1)

    def test_create_borrowing_with_invalid_data(self) -> None:
        book = sample_book(inventory=0)
        payload = {
            "borrow_date": "2023-10-10",
            "expected_return_date": "2023-10-20",
            "user": self.user.id,
            "book": book.id,
        }
        with self.assertRaises(ValidationError) as exc:
            response = self.client.post(BORROWING_URL, payload)
            self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("This book is currently out of stock", exc.exception)
        self.assertEqual(book.inventory, 0)

    def test_return_borrowing(self) -> None:
        borrowing = sample_borrowing(user=self.user)
        payload = {
            "actual_return_date": "2023-10-20"
        }
        url = f"{detail_url(borrowing.id)}return/"
        response = self.client.post(url, payload)
        book = Book.objects.last()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, INVENTORY + 1)

    def test_return_book_twice_not_allowed(self) -> None:
        borrowing = sample_borrowing(
            user=self.user,
            actual_return_date="2023-10-15"
        )
        payload = {
            "actual_return_date": "2023-10-20"
        }
        url = f"{detail_url(borrowing.id)}return/"
        book = Book.objects.last()
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(book.inventory, INVENTORY)

    def test_update_borrowing_not_allowed(self) -> None:
        borrowing = sample_borrowing(
            user=self.user
        )
        payload = {
            "expected_return_date": "2023-10-30"
        }
        url = detail_url(borrowing.id)
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_borrowing_not_allowed(self) -> None:
        borrowing = sample_borrowing(
            user=self.user
        )
        url = detail_url(borrowing.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_active_borrowings(self) -> None:
        borrowing = sample_borrowing(
            user=self.user,
            actual_return_date="2023-10-20"
        )

        serializer = BorrowingSerializer(borrowing)
        response = self.client.get(BORROWING_URL, {"is_active": 1})

        self.assertNotIn(serializer.data, response.data)

    def test_filter_by_user_not_allowed(self) -> None:
        user_2 = get_user_model().objects.create_user(
            "another@user.com",
            "another_password12345"
        )
        borrowing = sample_borrowing(
            user=user_2,
            actual_return_date="2023-10-20"
        )
        response = self.client.get(BORROWING_URL, {"user_id": user_2.id})
        serializer = BorrowingSerializer(borrowing)

        self.assertNotIn(serializer.data, response.data)


class AdminBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_admin_can_update_borrowing(self) -> None:
        borrowing = sample_borrowing(user=self.user)
        payload = {
            "expected_return_date": "2023-10-30"
        }
        url = detail_url(borrowing.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_borrowing(self) -> None:
        borrowing = sample_borrowing(user=self.user)
        url = detail_url(borrowing.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
