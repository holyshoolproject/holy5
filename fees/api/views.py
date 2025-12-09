from rest_framework import viewsets
from ..models import FeeStructure, StudentFeeRecord, Payment
from .ses import (
    FeeStructureSerializer,
    StudentFeeRecordSerializer,
    PaymentSerializer
)
from django.db.models import Count, F, Q

from rest_framework.response import Response
from django.urls import reverse



from rest_framework import viewsets


from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer

    @action(detail=False, methods=['get'])
    def common_fee_categories(self, request):
        data = (
            self.queryset
            .values("grade_class__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def discounts_applied(self, request):
        discounted = self.queryset.filter(is_discounted=True).count()
        total = self.queryset.count()
        return Response({
            "total_fee_structures": total,
            "discounted_fee_structures": discounted,
            "percentage_discounted": (discounted / total * 100) if total > 0 else 0
        })



from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, F

class StudentFeeRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentFeeRecord.objects.all()
    serializer_class = StudentFeeRecordSerializer

    # 1. Expected fees per term
    @action(detail=False, methods=['get'])
    def expected_fees(self, request):
        data = (
            FeeStructure.objects
            .values(
                academic_year_name=F("academic_year__name"),
                term_name=F("term__name"),
                grade_class_name=F("grade_class__name")
            )
            .annotate(
                total_students=Count("studentfeerecord"),
                expected_amount=F("amount") * Count("studentfeerecord")
            )
        )
        return Response(list(data))


    # 2. Total collected vs pending (overall)
    # 2. Total collected vs pending BY ACADEMIC YEAR + TERM
    @action(detail=False, methods=['get'])
    def collection_summary(self, request):

        data = (
            self.queryset
            .values(
                academic_year=F("fee_structure__academic_year__name"),
                term=F("fee_structure__term__name")
            )
            .annotate(
                total_collected=Sum("amount_paid"),
                total_pending=Sum("balance")
            )
            .order_by("academic_year", "term")
        )

        return Response(list(data))


    # 3. Percentage of unpaid students IN EACH CLASS
    from django.db.models import Count, F, Q

    @action(detail=False, methods=['get'])
    def unpaid_percentage_by_class(self, request):
        data = (
            self.queryset
            .values(class_name=F("fee_structure__grade_class__name"))
            .annotate(
                total_students=Count("id"),
                unpaid_students=Count("id", filter=Q(balance__gt=0)),
            )
            .annotate(
                unpaid_percentage=(F("unpaid_students") * 100.0) / F("total_students")
            )
            .order_by("class_name")
        )
        return Response(list(data))


    # 4. Highlight students with partial / overdue balances
    @action(detail=False, methods=['get'])
    def students_with_balance(self, request):
        qs = self.queryset.filter(balance__gt=0).select_related(
            "student", "fee_structure", "fee_structure__grade_class", "fee_structure__term"
        )

        data = [{
            "student": r.student.user.full_name,
            "class": r.fee_structure.grade_class.name,
            "term": r.fee_structure.term.name,
            "amount_paid": r.amount_paid,
            "balance": r.balance
        } for r in qs]

        return Response(data)

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

