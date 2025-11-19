from rest_framework import serializers
from ..models import (
    StudentProfile, GradeClass, AcademicYear, Term,
    StudentTermRecord, Subject, StudentSubjectRecord
)
from account.api.ses import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

from staff.api.ses import StaffProfileSerializer


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # nested user serializer
    currentClass = serializers.CharField(source="get_current_class_display_name", read_only=True)
    immunized = serializers.SerializerMethodField()
    allergies = serializers.SerializerMethodField()
    hasPeculiarHealthIssues = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "currentClass",
            "last_school_attended",
            "class_seeking_admission_to",
            "immunized",
            "allergies",
            "allergic_foods",
            "hasPeculiarHealthIssues",
            "health_issues",
            "other_related_info",
            "name_of_father",
            "name_of_mother",
            "occupation_of_father",
            "occupation_of_mother",
            "nationality_of_father",
            "nationality_of_mother",
            "contact_of_father",
            "contact_of_mother",
            "house_number"
        ]

    def get_immunized(self, obj):
        return obj.is_immunized.lower() == "yes" if obj.is_immunized else False

    def get_allergies(self, obj):
        return obj.has_allergies.lower() == "yes" if obj.has_allergies else False

    def get_hasPeculiarHealthIssues(self, obj):
        return obj.has_peculiar_health_issues.lower() == "yes" if obj.has_peculiar_health_issues else False


class GradeClassSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    
    class Meta:
        model = GradeClass
        fields = "__all__"


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class TermSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    
    class Meta:
        model = Term
        fields = "__all__"


class StudentTermRecordSerializer(serializers.ModelSerializer):
    class_meta_average = serializers.FloatField(
        source="calculate_average",
        read_only=True
    )

    class Meta:
        model = StudentTermRecord
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class StudentSubjectRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubjectRecord
        fields = "__all__"
        read_only_fields = ("total_score", "grade")
