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

"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from utils.mnotify_sms import send_sms_via_mnotify

@receiver(post_save, sender=Payment)
def send_payment_sms(sender, instance, created, **kwargs):
    if created:
        student = instance.student_fee_record.student
        parent_phone = student.contact_of_father
        print("Parent phone numberrrrrrr:", parent_phone)

        if not parent_phone:
            print("Parent phone number missing.")
            return

        message = (
    f"Dear {student.name_of_father if hasattr(student, 'name_of_father') else 'Parent'}, "
    f"thank you for making a payment of GHS {instance.amount} "
    f"for your child {student.user.full_name} ({instance.student_fee_record.fee_structure.term}). "
    f"Remaining balance: GHS {instance.student_fee_record.balance} - {instance.amount}. "
    f"Payment method: {instance.payment_method}. "
    f"We appreciate your support."
)


        print("SMS Message:", message)


        # Send SMS via mNotify
        #send_sms_via_mnotify([parent_phone], message)


"""