

from rest_framework import serializers

from staff.models import StaffProfile
from ..models import (
    StudentProfile, GradeClass, AcademicYear, Term, StaffProfile,
    StudentTermRecord, Subject, StudentSubjectRecord
)
from account.api.ses import UserSerializer, UserSerializerForPayments, UserSerializerForCreateUser
from django.contrib.auth import get_user_model

User = get_user_model()

from staff.api.ses import StaffProfileSerializer


class StudentProfileSerializerForPayments(serializers.ModelSerializer):
    user = UserSerializerForPayments(read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user"
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # nested user serializer
    current_class = serializers.CharField(source="get_current_class_display_name", read_only=True)
    immunized = serializers.SerializerMethodField()
    allergies = serializers.SerializerMethodField()
    hasPeculiarHealthIssues = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "is_discounted_student",           
            "current_class",
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


class StudentProfileCreateUserSerializer(serializers.ModelSerializer):
    user = UserSerializerForCreateUser()  # nested, not read-only

    class Meta:
        model = StudentProfile
        fields = ["id", "current_class", "is_discounted_student", "user", "last_school_attended", "class_seeking_admission_to", "is_immunized",
                  "has_allergies", "allergic_foods", "has_peculiar_health_issues", "health_issues",
                  "other_related_info", "name_of_father", "name_of_mother", "occupation_of_father",
                  "occupation_of_mother", "nationality_of_father", "nationality_of_mother",
                  "contact_of_father", "contact_of_mother", "house_number"]

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["current_class"] = instance.get_current_class_display_name()
        return data


    def create(self, validated_data):
        try:
            user_data = validated_data.pop("user")
            is_discounted_student = validated_data.get("is_discounted_student")
            print("is_discounted_student:", is_discounted_student)

            import random

            # generate unique user ID
            while True:
                user_id = str(random.randint(10000001, 99999999))
                if not User.objects.filter(user_id=user_id).exists():
                    break

            password = str(random.randint(1000, 9999))

            # create user
            user = User.objects.create(
                user_id=user_id,
                pin=password,
                full_name=user_data.get("full_name"),
                gender=user_data.get("gender").lower(),  # FIX
                date_of_birth=user_data.get("date_of_birth"),
                nationality=user_data.get("nationality"),
                role=user_data.get("role", "student").lower(),  # FIX
            )
            user.set_password(password)
            user.save()

            # update student profile
            profile = StudentProfile.objects.get(user=user)

            for key, value in validated_data.items():
                setattr(profile, key, value)

            profile.save()
            return profile

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise e
    
    def update(self, instance, validated_data):
        try:

            # Extract nested user data if present
            user_data = validated_data.pop("user", None)

            # Update StudentProfile fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update User fields if user_data exists
            if user_data:
                user = instance.user
                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()

            return instance

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise e



class LiteGradeClassSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = GradeClass
        fields = [
            "name"
        ]



class GradeClassSerializer(serializers.ModelSerializer):
    # Read: show the resolved staff (teacher) as a nested object
    staff = StaffProfileSerializer(read_only=True)

    # Write: accept a user_id from the frontend (NOT a staffprofile id)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = GradeClass
        fields = ["id", "name", "staff", "user_id"]

    def validate(self, attrs):

        """
        Map incoming user_id -> user.staff_profile and place it into attrs['staff'].
        This way, DRF will assign the FK correctly during create()/update().
        """
        user = attrs.pop("user_id", None)
        if user is None:
            # If staff is required in your business rule, raise here.
            # Your model has staff nullable (null=True), so only enforce if you want to.
            # raise serializers.ValidationError({"user_id": "This field is required."})
            return attrs  # allow creating/updating without a teacher if you want

        # Ensure the user has a staff_profile
        try:
            staff_profile = user.staff_profile
        except StaffProfile.DoesNotExist:
            raise serializers.ValidationError({"user_id": "Selected user has no associated staff profile."})

        # Inject the StaffProfile instance for the model FK
        attrs["staff"] = staff_profile
        return attrs

    def create(self, validated_data):
        # After validate(), validated_data has 'staff': <StaffProfile> when user_id was provided
        return GradeClass.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # If user_id was provided, validate() already swapped it to 'staff'
        staff = validated_data.get("staff", None)
        if staff is not None:
            instance.staff = staff

        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class LiteTermSerializer(serializers.ModelSerializer):
   
    
    class Meta:
        model = Term
        fields = [
            "name"
        ]


class TermSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), write_only=True
    )

    class Meta:
        model = Term
        fields = ["id", "name", "academic_year", "academic_year_id"]

    def create(self, validated_data):
        academic_year = validated_data.pop("academic_year_id")
        term = Term.objects.create(academic_year=academic_year, **validated_data)
        return term

    def update(self, instance, validated_data):
        academic_year = validated_data.pop("academic_year_id", None)

        if academic_year:
            instance.academic_year = academic_year
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


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
