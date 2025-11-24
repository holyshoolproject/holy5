# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializerForCreateUser(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)  # auto-generated
    password = serializers.CharField(write_only=True, required=False)  # optional, for DRF

    class Meta:
        model = User
        fields = ["user_id", "full_name", "gender", "date_of_birth", "nationality", "role", "password"]


class UserSerializerForPayments(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name"
        ]

        

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
