from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UserIdOrEmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        
        # Try login by user_id
        try:
            user = User.objects.get(user_id=username)
        except User.DoesNotExist:
            # Try login by email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        # Check password
        if user and user.check_password(password):
            return user

        return None
