# fees/signals.py

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.db import transaction

from .models import FeeStructure, StudentFeeRecord
from student.models import StudentTermRecord, StudentProfile


# -------------------------------------------------------
# 1. CREATE FEE RECORDS FOR REGULAR (NON-DISCOUNTED) STUDENTS
# -------------------------------------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FeeStructure, StudentProfile, StudentFeeRecord


@receiver(post_save, sender=FeeStructure)
def create_student_fee_records_for_regular(sender, instance, created, **kwargs):
    # Only run when a new FeeStructure is created
    if not created:
        return

    # If FeeStructure is meant ONLY for discounted students, skip this handler
    if instance.is_discounted:
        return

    print("Signal triggered for FeeStructure:", instance.id)

    # Fetch NON-DISCOUNTED students in this class
    students = StudentProfile.objects.filter(
        current_class=instance.grade_class_id,
        is_discounted_student=False
    )

    print("Found", students.count(), "students for FeeStructure", instance.id)

    # Create StudentFeeRecord for each non-discounted student
    for student in students:
        print("Creating fee record for:", student.user.full_name)

        StudentFeeRecord.objects.get_or_create(
            student=student,
            fee_structure=instance,
            defaults={
                "amount_paid": 0.00,
                "balance": instance.amount,
                "is_fully_paid": False,
            }
        )

# -------------------------------------------------------
# 2. CREATE FEE RECORDS FOR DISCOUNTED STUDENTS ADDED TO M2M FIELD
# -------------------------------------------------------
@receiver(m2m_changed, sender=FeeStructure.discounted_student_ids.through)
def create_student_fee_records_for_discounted(sender, instance, action, pk_set, **kwargs):
    if action != "post_add":
        return

    def _create():
        for student_id in pk_set:
            try:
                student = StudentProfile.objects.get(id=student_id)
            except StudentProfile.DoesNotExist:
                continue

            StudentFeeRecord.objects.get_or_create(
                student=student,
                fee_structure=instance,
                defaults={
                    "amount_paid": 0.00,
                    "balance": instance.amount,
                    "is_fully_paid": False,
                }
            )

    transaction.on_commit(_create)
