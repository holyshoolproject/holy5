from rest_framework.routers import DefaultRouter
from .view import StaffProfileViewSet

router = DefaultRouter()
router.register("staff-profiles", StaffProfileViewSet, basename="staff-profiles")

urlpatterns = router.urls
