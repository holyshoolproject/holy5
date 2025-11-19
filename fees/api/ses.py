from rest_framework import serializers
from ..models import FeeStructure, StudentFeeRecord, Payment
from student.api.ses import StudentProfileSerializer, AcademicYearSerializer, GradeClassSerializer, TermSerializer


# ---------------------------------------------------------
# FEE STRUCTURE SERIALIZER
# ---------------------------------------------------------
class FeeStructureSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    grade_class = GradeClassSerializer(read_only=True)
    term = TermSerializer(read_only=True)
 

    class Meta:
        model = FeeStructure
        fields = "__all__"


# ---------------------------------------------------------
# STUDENT FEE RECORD SERIALIZER
# ---------------------------------------------------------
class StudentFeeRecordSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    fee_structure = FeeStructureSerializer(read_only=True)



    class Meta:
        model = StudentFeeRecord
        fields = [
            "id",
            "student",
            "fee_structure",
            "amount_paid",
            "balance",
            "is_fully_paid",
            "date_created",

        ]
        read_only_fields = [
            "amount_paid",
            "balance",
            "is_fully_paid"
        ]

    def get_payments(self, obj):
        # Import inside method = NO circular import
        from .ses import PaymentSerializer
        payments = obj.payments.all()
        return PaymentSerializer(payments, many=True).data




class SimpleStudentFeeRecordSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    fee_structure = FeeStructureSerializer(read_only=True)
    class Meta:
        model = StudentFeeRecord
        fields = [
            "id",
            "student",
            "fee_structure",
            "amount_paid",
            "balance",
            "is_fully_paid",
        ]
        read_only_fields = ["amount_paid", "balance", "is_fully_paid"]


# ---------------------------------------------------------
# PAYMENT SERIALIZER
# ---------------------------------------------------------
class PaymentSerializer(serializers.ModelSerializer):
    # Avoid circular: show only ID for student_fee_record
    student_fee_record = SimpleStudentFeeRecordSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "student_fee_record",
            "date",
            "amount",
            "payment_method",
        ]
