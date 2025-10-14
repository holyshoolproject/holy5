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


from django.db.models.signals import post_save
from django.dispatch import receiver
from student.models import StudentProfile, StudentTermRecord
from .models import Term, GradeClass  


@receiver(post_save, sender=Term)
def create_student_term_records(sender, instance, created, **kwargs):
    if created:
        # When a new term is created
        students = StudentProfile.objects.filter(user__active=True)

        for student in students:
            # Try to find a GradeClass that matches the student's current_class name
            class_number = student.current_class
            class_name_map = dict(StudentProfile.CURRENT_CLASS_CHOICES)
            class_name = class_name_map.get(class_number)

            grade_class = GradeClass.objects.filter(name__iexact=class_name).first()

            if grade_class:
                StudentTermRecord.objects.get_or_create(
                    student=student,
                    term=instance,
                    defaults={
                        'grade_class': grade_class
                    }
                )
