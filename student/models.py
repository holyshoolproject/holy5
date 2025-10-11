from django.db import models
from staff.models import StaffProfile
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class StudentProfile(models.Model):

    YES_NO_CHOICES = [
        ('yes', 'yes'),
        ('no', 'no'),
    ]

    CLASS_CHOICES = [
        ('creche', 'creche'),
        ('nursery 1', 'nursery 1'),
        ('nursery 2', 'nursery 2'),
        ('kg 1', 'kg 1'),
        ('kg 2', 'kg 2'),
        ('class 1', 'class 1'),
        ('class 2', 'class 2'),
        ('class 3', 'class 3'),
        ('class 4', 'class 4'),
        ('class 5', 'class 5'),
        ('class 6', 'class 6'),
        ('jhs 1', 'jhs 1'),
        ('jhs 2', 'jhs 2'),
        ('jhs 3', 'jhs 3'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    last_school_attended = models.CharField(max_length=255, null=True, blank=True)
    class_seeking_admission_to = models.CharField(max_length=20, choices=CLASS_CHOICES, null=True, blank=True)
    is_immunized = models.CharField(max_length=200, null=True, blank=True)
    has_allergies = models.CharField(max_length=10, choices=YES_NO_CHOICES, null=True, blank=True)
    allergic_foods = models.CharField(max_length=300, null=True, blank=True)
    has_peculiar_health_issues = models.CharField(max_length=10, choices=YES_NO_CHOICES, null=True, blank=True)
    health_issues = models.CharField(max_length = 150, null=True, blank=True)
    other_related_info = models.TextField(null=True, blank=True)

    name_of_father = models.CharField(max_length=100, null=True, blank=True)
    name_of_mother = models.CharField(max_length=100, null=True, blank=True)

    occupation_of_father = models.CharField(max_length=100 , null=True, blank=True)
    occupation_of_mother = models.CharField(max_length=100, null=True, blank=True)

    nationality_of_father = models.CharField(max_length=100, null=True, blank=True)
    nationality_of_mother  = models.CharField(max_length=100, null=True, blank=True)

    contact_of_father =  models.CharField(max_length=100, null=True, blank=True)
    contact_of_mother =  models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.full_name 


class GradeClass(models.Model):
    CLASS_CHOICES = [
        ('creche', 'creche'),
        ('nursery 1', 'nursery 1'),
        ('nursery 2', 'nursery 2'),
        ('kg 1', 'kg 1'),
        ('kg 2', 'kg 2'),
        ('class 1', 'class 1'),
        ('class 2', 'class 2'),
        ('class 3', 'class 3'),
        ('class 4', 'class 4'),
        ('class 5', 'class 5'),
        ('class 6', 'class 6'),
        ('jhs 1', 'jhs 1'),
        ('jhs 2', 'jhs 2'),
        ('jhs 3', 'jhs 3'),
    ]
    name = models.CharField(choices=CLASS_CHOICES, max_length=40, verbose_name="Class")
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Teacher") 

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        
    def __str__(self):
        return self.name

# -------------------
# ACADEMIC YEAR
# -------------------


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name



# -------------------
# TERMS
# -------------------

class Term(models.Model):
    TERM_CHOICES = [
        ("1st Term", "1st Term"),
        ("2nd Term", "2nd Term"),
        ("3rd Term", "3rd Term"),
    ]
    name = models.CharField(max_length=20, choices=TERM_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"




class StudentTermRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    grade_class = models.ForeignKey(GradeClass, on_delete=models.SET_NULL, null=True, verbose_name="Class")

    attendance = models.IntegerField(default=0)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "term")

    def __str__(self):
        return f"{self.student} - {self.grade_class} - {self.term}"

    def calculate_average(self):
        """Average across all subjects"""
        subject_records = self.subjects.all()
        if subject_records:
            return sum(s.total_score for s in subject_records) / subject_records.count()
        return 0



class Subject(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class StudentSubjectRecord(models.Model):
    student_term_record = models.ForeignKey("StudentTermRecord", on_delete=models.CASCADE, related_name="subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class_score = models.FloatField(default=0)   # e.g., 30/40
    exam_score = models.FloatField(default=0)    # e.g., 60/60
    total_score = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. calculate total
        self.total_score = self.class_score + self.exam_score

        # 2. assign grade automatically
        self.grade = self.calculate_grade(self.total_score)

        super().save(*args, **kwargs)

    def calculate_grade(self, total):
        """
        Example grading system (adjust as needed):
        80 - 100 = A
        70 - 79  = B
        60 - 69  = C
        50 - 59  = D
        <50      = F
        """
        if total >= 80:
            return "A"
        elif total >= 70:
            return "B"
        elif total >= 60:
            return "C"
        elif total >= 50:
            return "D"
        return "F"

    def __str__(self):
        return f"{self.student_term_record.student} - {self.subject} ({self.grade})"



# --------------------- FEE STRUCTURE ---------------------

from django.utils import timezone


# -----------------------
# FEE STRUCTURE
# -----------------------
class FeeStructure(models.Model):
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)
    grade_class = models.ForeignKey("GradeClass", on_delete=models.CASCADE)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # e.g. 1200.00

    class Meta:
        unique_together = ('academic_year', 'grade_class', 'term')

    def __str__(self):
        return f"{self.grade_class} - {self.term} ({self.academic_year}) — {self.amount} GHS"


# -----------------------
# STUDENT FEE RECORD
# -----------------------
class StudentFeeRecord(models.Model):
    student = models.ForeignKey("StudentProfile", on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_fully_paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'fee_structure')

    def __str__(self):
        fs = self.fee_structure
        return f"{self.student.user.full_name} - {fs.term} ({fs.academic_year})"

    def save(self, *args, **kwargs):
        # Automatically calculate balance and full payment status
        self.balance = self.fee_structure.amount - self.amount_paid
        self.is_fully_paid = self.balance <= 0
        super().save(*args, **kwargs)

    def total_arrears(self):
        """
        Total unpaid fees across all terms in the same academic year.
        """
        fs = self.fee_structure
        arrears = StudentFeeRecord.objects.filter(
            student=self.student,
            fee_structure__academic_year=fs.academic_year,
            balance__gt=0
        ).exclude(id=self.id)
        return sum(r.balance for r in arrears)


# -----------------------
# PAYMENT MODEL
# -----------------------
class Payment(models.Model):
    student_fee_record = models.ForeignKey(StudentFeeRecord, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g. Cash, MOMO, Bank
    reference = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.student_fee_record.student.user.full_name} - {self.amount} GHS"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update total payments and balances
        record = self.student_fee_record
        record.amount_paid = sum(p.amount for p in record.payments.all())
        record.save()
