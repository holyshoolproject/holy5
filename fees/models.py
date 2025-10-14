from django.db import models
from student.models import StudentProfile, GradeClass, AcademicYear, Term    

# Create your models here.
# --------------------- FEE STRUCTURE ---------------------

from django.utils import timezone
from decimal import Decimal


# -----------------------
# FEE STRUCTURE
# -----------------------
class FeeStructure(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade_class = models.ForeignKey(GradeClass, on_delete=models.CASCADE)
    term = models.ForeignKey("student.Term", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # e.g. 1200.00

    class Meta:

        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
        unique_together = ('academic_year', 'grade_class', 'term')

    def __str__(self):
        return f"{self.grade_class} - {self.term}  — {self.amount} GHS"



# -----------------------
from decimal import Decimal
from django.db import models
from django.utils import timezone
from threading import Thread
import requests

from student.models import StudentProfile
from fees.models import FeeStructure

import requests
import json

def send_sms(recipient, message):
    """Send SMS via MNotify API with error handling and clear feedback."""
    endPoint = 'https://api.mnotify.com/api/sms/quick'
    apiKey = 'CelTN4i2JFPI2ZpknqYl0azod'  
    url = f'{endPoint}?key={apiKey}'

    data = {
        "recipient": [recipient],
        "sender": "KingOfGlory",  # must be a verified sender ID on MNotify
        "message": message,
        "is_schedule": False,
        "schedule_date": "",
  
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        # Raise error if response is not 2xx
        response.raise_for_status()

        result = response.json()
        print("✅ SMS sent successfully:", json.dumps(result, indent=2))

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error ({response.status_code}): {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Unable to reach MNotify servers.")

    except requests.exceptions.Timeout:
        print("❌ Timeout: MNotify API took too long to respond.")

    except Exception as e:
        print(f"❌ Unexpected error while sending SMS: {e}")

# -----------------------------
# Student Fee Record Model
# -----------------------------

class StudentFeeRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_fully_paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Student Fee Record'
        verbose_name_plural = 'Student Fee Records'
        unique_together = ('student', 'fee_structure')

    def update_balance(self, new_payment):
        """Update totals when a new payment is added."""
        new_payment = Decimal(new_payment)
        total_fee = Decimal(str(self.fee_structure.amount))

        # Update totals
        self.amount_paid += new_payment
        self.balance = total_fee - self.amount_paid
        self.is_fully_paid = self.balance <= 0
        self.save(update_fields=["amount_paid", "balance", "is_fully_paid"])

    def save(self, *args, **kwargs):
        """Ensure balance and full payment are consistent before saving."""
        if not isinstance(self.amount_paid, Decimal):
            self.amount_paid = Decimal(str(self.amount_paid))

        total_fee = Decimal(str(self.fee_structure.amount))
        self.balance = total_fee - self.amount_paid
        self.is_fully_paid = self.balance <= 0

        super().save(*args, **kwargs)

    def total_arrears(self):
        """Total unpaid fees across all terms in the same academic year."""
        fs = self.fee_structure
        arrears = StudentFeeRecord.objects.filter(
            student=self.student,
            fee_structure__academic_year=fs.academic_year,
            balance__gt=0
        ).exclude(id=self.id)
        return sum(r.balance for r in arrears)

    def __str__(self):
        fs = self.fee_structure
        academic_year = getattr(fs, 'academic_year', None)
        term = getattr(fs, 'term', None)
        grade_class = getattr(fs, 'grade_class', None)
        term_name = term.name if term else "No Term"
        return f"{self.student.user.full_name} - {term_name} | {academic_year} | {grade_class}"


# -----------------------------
# Payment Model (with SMS)
# -----------------------------
class Payment(models.Model):
    student_fee_record = models.ForeignKey(StudentFeeRecord, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g. Cash, MOMO, Bank

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.student_fee_record.student.user.full_name} - {self.amount} GHS"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            record = self.student_fee_record
            record.update_balance(self.amount)

            # Prepare SMS message
            student = record.student
            parent_phone = student.contact_of_father  

            if record.balance > 0:
                payment_status = "part payment"
            else:
                payment_status = "full payment"

                # ₵

            message = (
                f"Dear Parent/Guardian,\n"
                f"You made a {payment_status} of GH₵ {self.amount} for your ward, {student.user.full_name}.\n"
                f"Purpose: School fees\n"
                f"Class/Term: {record.fee_structure.grade_class} – {record.fee_structure.term} academic year.\n"
                f"Balance: GH₵ {record.balance}.\n"
                f"Thank you."
            )




            print("Prepared SMS message:", message)
            print("Parent phone number:", parent_phone)
            print("Student name:", student)

            # Send SMS asynchronously so it doesn't block the save
            if parent_phone:
                print("Sending SMS...")
                print(message)
                Thread(target=send_sms, args=(parent_phone, message)).start()
