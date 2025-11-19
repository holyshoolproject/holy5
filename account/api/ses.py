# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "user_id",        # or whatever your User model field is
            "full_name",
            "role",
            "gender",
            "nationality",
            "is_active",
            "is_staff",
            "date_of_birth",

        ]
