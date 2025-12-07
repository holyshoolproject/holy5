from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError("The User ID must be set")
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)  # password could be a PIN
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(user_id, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('student', 'student'),
        ('staff', 'staff'),
        ('principal', 'principal'),
        ('administrator', 'administrator'),

    ]

    GENDER_CHOICES = [
        ('male', 'male'),
        ('female', 'female'),       

    ]

    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    pin = models.CharField(max_length=20, null=True, blank=True)
    user_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=222)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10,null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True) 

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.full_name} ({self.role}) ({self.user_id})"

