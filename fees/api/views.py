from rest_framework import viewsets
from ..models import FeeStructure, StudentFeeRecord, Payment
from .ses import (
    FeeStructureSerializer,
    StudentFeeRecordSerializer,
    PaymentSerializer
)

from rest_framework.response import Response
from django.urls import reverse



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
    
    def create(self, request, *args, **kwargs):
            print("Creating Payment with data:", request.data)
            response = super().create(request, *args, **kwargs)
            payment_id = response.data.get('id')
            if payment_id:               
                
                response.data['receipt_url'] = request.build_absolute_uri(
                    reverse('payment-receipt', kwargs={'pk': payment_id})
                )

            return response

