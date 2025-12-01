
from rest_framework import serializers

from student.models import StudentProfile
from ..models import FeeStructure, StudentFeeRecord, Payment
from student.api.ses import (
    StudentProfileSerializer,
    AcademicYearSerializer,
    GradeClassSerializer,
    TermSerializer,
    StudentProfileSerializerForPayments,
    LiteGradeClassSerializer,
    LiteTermSerializer,
)

# ---------------------------------------------------------
# FEE STRUCTURE SERIALIZERS
# ---------------------------------------------------------
class LiteFeeStructureSerializer(serializers.ModelSerializer):
    """
    Lightweight FeeStructure serializer used inside nested responses to
    avoid deep graphs and performance issues.
    """
    grade_class = LiteGradeClassSerializer(read_only=True)
    term = LiteTermSerializer(read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = FeeStructure
        fields = "__all__"


class FeeStructureSerializer(serializers.ModelSerializer):
    """
    Full FeeStructure serializer for detailed views / forms.
    """
    academic_year = AcademicYearSerializer(read_only=True)
    grade_class = GradeClassSerializer(read_only=True)
    term = TermSerializer(read_only=True)

    academic_year_id = serializers.IntegerField(write_only=True)
    grade_class_id = serializers.IntegerField(write_only=True)
    term_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FeeStructure
        fields = "__all__"


# ---------------------------------------------------------
# STUDENT FEE RECORD SERIALIZERS
# ---------------------------------------------------------
class StudentFeeRecordSerializer(serializers.ModelSerializer):
    """
    Used when creating or listing StudentFeeRecords directly.
    Keeps student and fee_structure lightweight for performance.
    """
    student = StudentProfileSerializerForPayments(read_only=True)
    fee_structure = LiteFeeStructureSerializer(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), write_only=True
    )
    fee_structure_id = serializers.PrimaryKeyRelatedField(
        queryset=FeeStructure.objects.all(), write_only=True
    )

    class Meta:
        model = StudentFeeRecord
        fields = [
            "id",
            "student",
            "fee_structure",
            "student_id",
            "fee_structure_id",
            "amount_paid",
            "balance",
            "is_fully_paid",
            "date_created",
        ]
        read_only_fields = [
            "amount_paid",
            "balance",
            "is_fully_paid",
        ]

    def create(self, validated_data):
        # Incoming payload from frontend (for visibility during debugging)


        # Pop the IDs to assign FK relations
        student = validated_data.pop("student_id")
        fee_structure = validated_data.pop("fee_structure_id")

        # Create the StudentFeeRecord
        record = StudentFeeRecord.objects.create(
            student=student,
            fee_structure=fee_structure,
            **validated_data
        )
        return record


class SimpleStudentFeeRecordSerializer(serializers.ModelSerializer):
    """
    Used as a nested serializer inside PaymentSerializer.
    IMPORTANT CHANGE: fee_structure now uses LiteFeeStructureSerializer
    to reduce nested depth (prevents N+1 queries and timeouts).
    """
    student = StudentProfileSerializerForPayments(read_only=True)
    fee_structure = LiteFeeStructureSerializer(read_only=True)  # <-- changed from full FeeStructureSerializer

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
    """
    Payment serializer with write-only FK ID (student_fee_record_id)
    and a read-only nested SimpleStudentFeeRecord.
    """
    # Make date robust; allow it to be omitted or null from frontend
    date = serializers.DateField(required=False, allow_null=True)

    # Avoid circular references: write-only ID used to create the FK
    student_fee_record_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentFeeRecord.objects.all(), write_only=True
    )

    # Read-only nested representation for the frontend
    student_fee_record = SimpleStudentFeeRecordSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "student_fee_record_id",  # write-only FK input
            "student_fee_record",     # read-only nested output
            "date",
            "amount",
            "payment_method",
        ]

    def create(self, validated_data):
        # Incoming payload from frontend (for visibility during debugging)
  

        # Pop the write-only FK ID and attach the relation
        student_fee_record = validated_data.pop("student_fee_record_id")

        # Create the payment
        pay = Payment.objects.create(
            student_fee_record=student_fee_record,
            **validated_data
        )
        return pay
