from rest_framework.routers import DefaultRouter
from .views import FamilyViewSet, FamilyFeeRecordViewSet, FamilyPaymentViewSet

router = DefaultRouter()
router.register("families", FamilyViewSet)
router.register("family-fee-records", FamilyFeeRecordViewSet)
router.register("family-payments", FamilyPaymentViewSet)

urlpatterns = router.urls
