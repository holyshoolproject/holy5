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
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """
        Optimize Payment queryset by eager-loading all related objects
        used in nested serializers to prevent N+1 queries and timeouts.
        """
        return (
            
            Payment.objects.select_related(
                "student_fee_record",
                "student_fee_record__student",  # StudentProfile
                "student_fee_record__fee_structure",
                "student_fee_record__fee_structure__grade_class",
                "student_fee_record__fee_structure__term",
                "student_fee_record__fee_structure__academic_year",
            )

        )
