# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
User = get_user_model()
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


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
class AdministratorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # Accept email from frontend

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "gender",
            "date_of_birth",
            "is_active",
            "role",
            "password",
            "email",  # include email
        ]
        extra_kwargs = {
            "role": {"read_only": True},
            "password": {"write_only": True, "required": False},
        }

    def create(self, validated_data):
        email = validated_data.pop("email")  # get email
        validated_data.pop("user_id", None)  # remove user_id if present
        validated_data.pop("role", None)     # force role
        password = validated_data.pop("password", "TempPassword123!")

        user = User.objects.create(
            user_id=email,
            email=email,
            role="administrator",
            password=password,
            **validated_data
        )
         # Set the password properly
        user.set_password(password)
        user.save()
        return user


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
            "email",    

        ]

# FOR AUTHS

class UserLoginSerializer(serializers.Serializer):
    role = serializers.CharField(required=True)
    login_id = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        min_length=4,
        max_length=128,
        style={'input_type': 'password'},
        trim_whitespace=True,
         error_messages={
            "min_length": "Password must be more than 3 characters.",
            "required": "Password is required.",
        }
    )

    def validate(self, attrs):
        login_id = attrs.get('login_id')
        password = attrs.get('password')
        role = attrs.get('role')

        if not login_id or not password:
            raise serializers.ValidationError("Both login ID and password are required")

        # Authenticate
        user = authenticate(username=login_id, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Your account is disabled")

        # Ensure role was provided
        if not role:
            raise serializers.ValidationError("Role is required")

        # Ensure user has the claimed role
        if user.role != role:
            raise serializers.ValidationError("You are not authorized to log in as this role")

        attrs['user'] = user
        return attrs



class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        uidb64 = attrs.get("uidb64")
        token = attrs.get("token")
        password1 = attrs.get("new_password1")
        password2 = attrs.get("new_password2")

        # Check if passwords match
        if password1 != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Decode user
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid user ID."})

        # Validate token
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        # Attach user for later use
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        password = self.validated_data["new_password1"]
        user = self.validated_data["user"]
        user.set_password(password)
        user.save()
        return {"detail": "Password has been reset successfully."}



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)


    def validate_old_password(self, value):
        user =  self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirm password do not match")
        
        validate_password(new_password)
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate that the email exists in the database.
        """
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # Even if the email doesn't exist, return a generic message for security
            pass
        return value

    def save(self, request):
        email = self.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            print("Found user :", user)  # Debug log
            print("User email :", user.email)  # Debug log
            print("User ID :", user.id)  # Debug log

            # Generate UID and token for the actual user
            uidb64 = urlsafe_base64_encode(force_bytes(str(user.pk)))
            print("Generated UID:", uidb64)

            token = default_token_generator.make_token(user)
            reset_url = f"http://localhost:3000/#/reset-password-confirm/{uidb64}/{token}/"
            #reset_url = f"http://localhost:3000/reset-password-confirm/{uidb64}/{token}/"



            # Choose environment reset URL
            # Production


            #reset_url = f"https://lands-ui.vercel.app/password-reset-confirm/{uid}/{token}/" # should always point to frontend so use front end url. not backend



          
            # Localhost (uncomment to use locally)
            # reset_url = f"http://localhost:8080/password-reset-confirm/{uid}/{token}/"

            # Send email
            send_mail(
                subject="Password Reset Request",
                message=(
                    f"Hi,\n\n"
                    f"We received a request to reset your password. "
                    f"Click the link below to reset it:\n\n{reset_url}\n\n"
                    f"If you didn’t request this, you can ignore this email."
                ),
                from_email="phevab1@gmail.com",
                recipient_list=[email],
                fail_silently=False,
            )

        except User.DoesNotExist:
            # If the user doesn't exist, skip sending the email but return the same response
            pass
        except Exception as e:
            raise  # Let the view handle unexpected errors

        # Always return a generic response to avoid leaking whether the email exists
        return {
            "detail": "If this email exists, you’ll receive a password reset link. "
                      "If you didn’t request this, you can ignore the email."
        }



