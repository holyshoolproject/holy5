# fees/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FeeStructure, StudentFeeRecord
from student.models import StudentTermRecord  # adjust path if different


@receiver(post_save, sender=FeeStructure)
def create_student_fee_records(sender, instance, created, **kwargs):
    """Auto-create StudentFeeRecord for all students in that class and term."""
    if created:
        grade_class = instance.grade_class
        term = instance.term
        academic_year = instance.academic_year

        # Get all student term records that match this structure
        term_records = StudentTermRecord.objects.filter(
            grade_class=grade_class,
            term=term
        )

        count = 0
        for record in term_records:
            StudentFeeRecord.objects.get_or_create(
                student=record.student, 
        
                fee_structure=instance
            )
            count += 1
