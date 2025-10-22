from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from student.models import Term, AcademicYear
from fees.models import StudentFeeRecord
from threading import Thread
from fees.models import send_sms  # import your existing send_sms helper

User = get_user_model()


class Family(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(User, related_name="family_members")

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"

    def __str__(self):
        return self.name

    def member_names(self):
        return ", ".join(user.full_name for user in self.members.all())

from decimal import Decimal

class FamilyFeeRecord(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    is_fully_paid = models.BooleanField(default=False)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Family Fee Record'
        verbose_name_plural = 'Family Fee Records'
        unique_together = ('family', 'term', 'academic_year')

    def __str__(self):
        return f"{self.family.name} | {self.term.name} | {self.academic_year.name}"

    def save(self, *args, **kwargs):
        """Ensure balance and full payment consistency before saving."""
        if not isinstance(self.amount_paid, Decimal):
            self.amount_paid = Decimal(str(self.amount_paid))
        if not isinstance(self.amount_to_pay, Decimal):
            self.amount_to_pay = Decimal(str(self.amount_to_pay))

        # Calculate balance and payment status
        self.balance = self.amount_to_pay - self.amount_paid
        self.is_fully_paid = self.balance <= 0

        # Optionally clear related student records (if needed)
        member_ids = self.family.members.values_list("id", flat=True)
        StudentFeeRecord.objects.filter(student__user_id__in=member_ids).delete()

        super().save(*args, **kwargs)

    def update_balance(self, payment_amount):
        """Update totals when a new family payment is made."""
        payment_amount = Decimal(payment_amount)
        self.amount_paid += payment_amount
        self.balance = self.amount_to_pay - self.amount_paid
        self.is_fully_paid = self.balance <= 0
        self.save(update_fields=["amount_paid", "balance", "is_fully_paid"])


class FamilyPayment(models.Model):
    family_fee_record = models.ForeignKey(
        FamilyFeeRecord, on_delete=models.CASCADE, related_name="payments"
    )
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., Cash, MOMO, Bank

    class Meta:
        verbose_name = "Family Payment"
        verbose_name_plural = "Family Payments"

    def __str__(self):
        return f"{self.family_fee_record.family.name} - {self.amount} GHS"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            record = self.family_fee_record
            record.update_balance(self.amount)

            # Build the family payment message
            family = record.family
            student_names = ", ".join(u.full_name.title() for u in family.members.all())

            if record.balance > 0:
                payment_status = "part payment"
            else:
                payment_status = "full payment"

            message = (
                f"Dear Parent/Guardian,\n"
                f"You made a {payment_status} of GH₵ {self.amount} for your wards: {student_names}.\n"
                f"Purpose: School Fees\n"
                f"Term/Year: {record.term.name} – {record.academic_year.name}.\n"
                f"Balance: GH₵ {record.balance}.\n"
                f"Thank you."
            )

            print("Prepared SMS message")
            print("-------------------------------------------------------")
            print(message)
            print("-------------------------------------------------------")


    # Send SMS once to the father's phone (first student's father)
            first_member = family.members.first()
            if first_member and hasattr(first_member, "student_profile"):
                parent_phone = first_member.student_profile.contact_of_father
                if parent_phone:
                    print("sent to:", parent_phone)
                    Thread(target=send_sms, args=(parent_phone, message)).start()