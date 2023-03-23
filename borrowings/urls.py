from rest_framework import routers
from borrowings.models import Borrowing


router = routers.DefaultRouter()
router.register(Borrowing)

urlpatterns = router.urls

app_name = "borrowings"
