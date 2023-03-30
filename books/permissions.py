from rest_framework.permissions import SAFE_METHODS, IsAdminUser
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class IsAdminUserOrReadOnly(IsAdminUser):
    """Read only permission for all not-admin users"""

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin
