from rest_framework import serializers
from ..models import StaffProfile
from django.contrib.auth import get_user_model
from account.api.ses import UserSerializer

User = get_user_model()



class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StaffProfile
        fields = ["id", "user"]
