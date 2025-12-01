# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializerForCreateUser(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)  # auto-generated
    password = serializers.CharField(write_only=True, required=False)  # optional, for DRF

    def validate_gender(self, value):
        return value.lower().strip() 
    
    class Meta:
        model = User
        fields = ["id", "user_id", "pin", "full_name", "gender", "date_of_birth", "nationality", "role", "password", "is_active"]


class UserSerializerForPayments(serializers.ModelSerializer):

    def validate_gender(self, value):
        return value.lower().strip() 
    
    
    class Meta:
        model = User
        fields = [
            "full_name"
        ]
    

        

class UserSerializer(serializers.ModelSerializer):

    def validate_gender(self, value):
        return value.lower().strip() 
    

    class Meta:
        model = User
        fields = [
            "id",
            "user_id", 
            "pin",      
            "full_name",
            "role",
            "gender",
            "nationality",
            "is_active",
            "is_staff",
            "date_of_birth",

        ]
