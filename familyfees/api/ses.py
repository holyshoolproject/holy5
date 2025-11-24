from rest_framework import serializers
from ..models import Family, FamilyFeeRecord, FamilyPayment
from django.contrib.auth import get_user_model
from student.api.ses import AcademicYearSerializer, TermSerializer
from student.models import StudentProfile, Term, AcademicYear
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name"]


class FamilySerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    # Accept user IDs during creation/update
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=User.objects.all(),
        source="members",
    )

    class Meta:
        model = Family
        fields = ["id", "name", "members", "member_ids"]

    def create(self, validated_data):
        # Extract member IDs from payload
        members = validated_data.pop("members", [])

        # Create the family
        family = Family.objects.create(**validated_data)

        # Assign members (many-to-many)
        family.members.set(members)

        return family

    def update(self, instance, validated_data):
        # Extract member IDs if provided
        members = validated_data.pop("members", None)

        # Update simple fields
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        # Update members only if provided
        if members is not None:
            instance.members.set(members)

        return instance


class FamilyFeeRecordSerializer(serializers.ModelSerializer):
    family = FamilySerializer(read_only=True)    
    term = TermSerializer(read_only = True)
    academic_year = AcademicYearSerializer(read_only=True)

    family_id = serializers.PrimaryKeyRelatedField(
        queryset=Family.objects.all(), write_only=True, source="family"
    )

    term_id = serializers.PrimaryKeyRelatedField(
        queryset=Term.objects.all(), write_only=True, source="term"
    )

    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), write_only=True, source="academic_year"
    )


    class Meta:
        model = FamilyFeeRecord
        fields = [
            "family_id",
            "term_id",
            "academic_year_id",
            "id",
            "family",
            "family_id",
            "amount_to_pay",
            "amount_paid",
            "balance",
            "is_fully_paid",
            "term",
            "academic_year",
            "date_created",
        ]
        read_only_fields = ["balance", "is_fully_paid"]


class FamilyPaymentSerializer(serializers.ModelSerializer):
    family_fee_record = FamilyFeeRecordSerializer(read_only=True)
    family_fee_record_id = serializers.PrimaryKeyRelatedField(
        queryset=FamilyFeeRecord.objects.all(),
        write_only=True,
        source="family_fee_record",
    )

    class Meta:
        model = FamilyPayment
        fields = [
            "id",
            "family_fee_record",
            "family_fee_record_id",
            "date",
            "amount",
            "payment_method",
        ]
