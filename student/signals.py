from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AcademicYear  # adjust path if needed
from student.models import StudentProfile

@receiver(post_save, sender=AcademicYear)
def promote_students_on_new_year(sender, instance, created, **kwargs):
    if created:
        students = StudentProfile.objects.select_related('user').all()

        for student in students:
            if student.current_class < 14:
                # Promote to next class
                student.current_class += 1
                student.save()
            else:
                # Last class (JHS 3) — deactivate their user account
                student.user.active = False
                student.user.save()
