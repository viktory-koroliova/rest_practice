from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    """
    The request is authenticated as a user,
    or is a read-only for non-admin users.
    """

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        return bool(
            (
                request.method in ("GET", "POST")
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
