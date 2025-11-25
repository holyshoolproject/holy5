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

    CURRENT_CLASS_CHOICES = [
        (1, 'creche'),
        (2, 'nursery 1'),
        (3, 'nursery 2'),
        (4, 'kg 1'),
        (5, 'kg 2'),
        (6, 'class 1'),
        (7, 'class 2'),
        (8, 'class 3'),
        (9, 'class 4'),
        (10, 'class 5'),
        (11, 'class 6'),
        (12, 'jhs 1'),
        (13, 'jhs 2'),
        (14, 'jhs 3'),
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
    current_class = models.PositiveSmallIntegerField(choices=CURRENT_CLASS_CHOICES, default=1)

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

    house_number =  models.CharField(max_length=100, null=True, blank=True)

    def get_current_class_display_name(self):
        return dict(self.CURRENT_CLASS_CHOICES).get(self.current_class, "Unknown")
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_current_class_display_name()}"



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
        ordering = ['-id']
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

    class Meta:
        ordering = ['-id']
        unique_together = ("name", "academic_year")

    def __str__(self):
        return f"{self.name} - ({self.academic_year})"




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



