from rest_framework.routers import DefaultRouter
from .views import (
    FeeStructureViewSet,
    StudentFeeRecordViewSet,
    PaymentViewSet
)

router = DefaultRouter()

router.register("fee-structures", FeeStructureViewSet, basename="fee-structures")
router.register("student-fee-records", StudentFeeRecordViewSet, basename="student-fee-records")
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = router.urls
