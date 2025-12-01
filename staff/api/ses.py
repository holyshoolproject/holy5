from rest_framework import serializers
from ..models import StaffProfile
from django.contrib.auth import get_user_model
from account.api.ses import UserSerializer, UserSerializerForCreateUser


User = get_user_model()

class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializerForCreateUser()  # Nested serializer for user

    class Meta:
        model = StaffProfile
        fields = ["id", "user"]

    def create(self, validated_data):
        try:
            user_data = validated_data.pop("user")

            # Generate unique user_id
            import random
            while True:
                user_id = str(random.randint(10000001, 99999999))
                if not User.objects.filter(user_id=user_id).exists():
                    break

            password = str(random.randint(1000, 9999))
            

            # Create user
            user = User.objects.create(
                user_id=user_id,
                pin=password,
                full_name=user_data.get("full_name"),
                gender=user_data.get("gender").lower(),
                date_of_birth=user_data.get("date_of_birth"),
                nationality=user_data.get("nationality"),
                role="staff",  # Force staff role
                is_staff=True
            )
            user.set_password(password)
            user.save()


                
    # Create or get staff profile
            staff_profile, _ = StaffProfile.objects.get_or_create(user=user)

            return staff_profile


        except Exception as e:
            import traceback

            traceback.print_exc()
            raise e

    def update(self, instance, validated_data):
        try:
            # Extract nested user data
            user_data = validated_data.pop("user", None)

            # Update StaffProfile fields (if any additional fields exist)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update User fields if user_data exists
            if user_data:
                user = instance.user
                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.role = "staff"  # Ensure role remains staff
                user.is_staff = True
                user.save()

            return instance

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise e
