import random
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import AcademicYear, StudentProfile

# Promotion mapping: current_class -> next_class
import random

PROMOTION_MAP = {
    2: 4,   # Nursery 1A -> Nursery 2A
    3: 5,   # Nursery 1B -> Nursery 2B

    4: 6,   # Nursery 2A -> KG 1A
    5: 7,   # Nursery 2B -> KG 1B

    6: 8,   # KG 1A -> KG 2A
    7: 9,   # KG 1B -> KG 2B

    8: 10,  # KG 2A -> Basic 1A
    9: 11,  # KG 2B -> Basic 1B

    10: 12, # Basic 1A -> Basic 2A
    11: 13, # Basic 1B -> Basic 2B

    12: 14, # Basic 2A -> Basic 3A
    13: 15, # Basic 2B -> Basic 3B

    14: 16, # Basic 3A -> Basic 4A
    15: 17, # Basic 3B -> Basic 4B

    16: 18, # Basic 4A -> Basic 5A
    17: 19, # Basic 4B -> Basic 5B

    18: 20, # Basic 5A -> Basic 6A
    19: 21, # Basic 5B -> Basic 6B

    20: 22, # Basic 6A -> Basic 7A
    21: 23, # Basic 6B -> Basic 7B

    22: 24, # Basic 7A -> Basic 8
    23: 24, # Basic 7B -> Basic 8

    24: 25, # Basic 8 -> Basic 9
}




# Reverse mapping for demotion. Because multiple previous classes can map to the same next class
# we pick a reasonable default when ambiguity exists (e.g., 20 -> 18). If you want perfect reversal
# you must store per-student history at promotion time.
REVERSE_PROMOTION_MAP = {
    2: 1,    # Nursery 1A -> Creche
    3: 1,    # Nursery 1B -> Creche

    4: 2,    # Nursery 2A -> Nursery 1A
    5: 3,    # Nursery 2B -> Nursery 1B

    6: 4,    # KG 1A -> Nursery 2A
    7: 5,    # KG 1B -> Nursery 2B

    8: 6,    # KG 2A -> KG 1A
    9: 7,    # KG 2B -> KG 1B

    10: 8,   # Basic 1A -> KG 2A
    11: 9,   # Basic 1B -> KG 2B

    12: 10,  # Basic 2A -> Basic 1A
    13: 11,  # Basic 2B -> Basic 1B

    14: 12,  # Basic 3A -> Basic 2A
    15: 13,  # Basic 3B -> Basic 2B

    16: 14,  # Basic 4A -> Basic 3A
    17: 15,  # Basic 4B -> Basic 3B

    18: 16,  # Basic 5A -> Basic 4A
    19: 17,  # Basic 5B -> Basic 4B

    20: 18,  # Basic 6A -> Basic 5A
    21: 19,  # Basic 6B -> Basic 5B

    22: 20,  # Basic 7A -> Basic 6A
    23: 21,  # Basic 7B -> Basic 6B

    24: 22,  # Basic 8 -> Basic 7A (default)
    25: 24,  # Basic 9 -> Basic 8
}


def promote_creche():
    """Randomly assign Creche children to Nursery 1A or 1B"""
    return random.choice([2, 3])
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import AcademicYear, StudentProfile

@receiver(post_save, sender=AcademicYear)
def promote_students_on_new_year(sender, instance, created, **kwargs):
    if not created:
        return

    students = StudentProfile.objects.select_related('user').all()

    with transaction.atomic():
        for student in students:
            current = student.current_class

            if current == 1:
                # Creche -> Nursery 1A/B randomly
                student.current_class = promote_creche()
                student.save()
                continue

            if current in PROMOTION_MAP:
                student.current_class = PROMOTION_MAP[current]
                student.save()
                continue

            if current == 25:
                # Basic 9 -> deactivate account
                user = getattr(student, "user", None)
                if user:
                    user.is_active = False
                    user.save()

@receiver(post_delete, sender=AcademicYear)
def reverse_students_on_year_delete(sender, instance, **kwargs):
    """
    Reverse promotions when AcademicYear is deleted.
    Cannot perfectly restore Creche split without history.
    """
    REVERSE_PROMOTION_MAP = {v: k for k, v in PROMOTION_MAP.items()}

    students = StudentProfile.objects.select_related('user').all()

    with transaction.atomic():
        for student in students:
            current = student.current_class

            # Reverse Creche assignment
            if current in (2, 3):
                student.current_class = 1
                student.save()
                continue

            if current in REVERSE_PROMOTION_MAP:
                student.current_class = REVERSE_PROMOTION_MAP[current]
                student.save()
                continue

            # If student was in Basic 9, demote to Basic 8
            if current == 25:
                student.current_class = 24
                student.save()
                continue

from django.db.models.signals import post_save
from django.dispatch import receiver
from student.models import StudentProfile, StudentTermRecord
from .models import Term, GradeClass  


@receiver(post_save, sender=Term)
def create_student_term_records(sender, instance, created, **kwargs):
    if created:
        # When a new term is created
        students = StudentProfile.objects.filter(user__is_active=True)

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
