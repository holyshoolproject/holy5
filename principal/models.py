from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class PrincipalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="principal_profile")
    def __str__(self):
        return self.user.full_name 