from rest_framework import viewsets
from ..models import Family, FamilyFeeRecord, FamilyPayment
from .ses import (
    FamilySerializer,
    FamilyFeeRecordSerializer,
    FamilyPaymentSerializer,
)


class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer


class FamilyFeeRecordViewSet(viewsets.ModelViewSet):
    queryset = FamilyFeeRecord.objects.select_related(
        "family", "term", "academic_year"
    )
    serializer_class = FamilyFeeRecordSerializer


class FamilyPaymentViewSet(viewsets.ModelViewSet):
    queryset = FamilyPayment.objects.select_related("family_fee_record")
    serializer_class = FamilyPaymentSerializer
