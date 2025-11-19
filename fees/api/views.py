from rest_framework import viewsets
from ..models import FeeStructure, StudentFeeRecord, Payment
from .ses import (
    FeeStructureSerializer,
    StudentFeeRecordSerializer,
    PaymentSerializer
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer


class StudentFeeRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentFeeRecord.objects.all()
    serializer_class = StudentFeeRecordSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
