from rest_framework import serializers

from student.models import StudentProfile
from ..models import FeeStructure, StudentFeeRecord, Payment
from student.api.ses import StudentProfileSerializer, AcademicYearSerializer, GradeClassSerializer, TermSerializer, StudentProfileSerializerForPayments, LiteGradeClassSerializer, LiteTermSerializer

# ---------------------------------------------------------
# FEE STRUCTURE SERIALIZER
# ---------------------------------------------------------
class LiteFeeStructureSerializer(serializers.ModelSerializer):
    grade_class = LiteGradeClassSerializer(read_only=True)
    term = LiteTermSerializer(read_only=True) 
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = FeeStructure
        fields = "__all__"



class FeeStructureSerializer(serializers.ModelSerializer):
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
# STUDENT FEE RECORD SERIALIZER
# ---------------------------------------------------------
class StudentFeeRecordSerializer(serializers.ModelSerializer):
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
        # Print incoming frontend data
        print("Frontend payload received in serializer:", validated_data)

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
    student = StudentProfileSerializerForPayments(read_only=True)
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
    date = serializers.DateField(required=False)
    
    # Avoid circular: show only ID for student_fee_record
    student_fee_record_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentFeeRecord.objects.all(), write_only=True
    )


    student_fee_record = SimpleStudentFeeRecordSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "student_fee_record_id",
            "student_fee_record",
            "date",
            "amount",
            "payment_method"
           
        ]
    
    def create(self, validated_data):
        # Print incoming frontend data
        print("Frontend payload received in serializer for payments:", validated_data)

        # Pop the IDs to assign FK relations
        student_fee_record = validated_data.pop("student_fee_record_id")
        
        # Create the payment
        pay = Payment.objects.create(
            student_fee_record=student_fee_record,
           
            **validated_data
        )

        return pay
