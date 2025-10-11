# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from student.models import StudentProfile
from staff.models import StaffProfile
from principal.models import PrincipalProfile
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'staff':
            StaffProfile.objects.create(user=instance)
        elif instance.role == 'principal':
            PrincipalProfile.objects.create(user=instance)
