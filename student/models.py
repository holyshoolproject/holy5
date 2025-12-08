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
    (1, 'Creche'),

    (2, 'Nursery 1A'),
    (3, 'Nursery 1B'),

    (4, 'Nursery 2A'),
    (5, 'Nursery 2B'),

    (6, 'KG 1A'),
    (7, 'KG 1B'),

    (8, 'KG 2A'),
    (9, 'KG 2B'),

    (10, 'Basic 1A'),
    (11, 'Basic 1B'),

    (12, 'Basic 2A'),
    (13, 'Basic 2B'),

    (14, 'Basic 3A'),
    (15, 'Basic 3B'),

    (16, 'Basic 4A'),
    (17, 'Basic 4B'),

    (18, 'Basic 5A'),
    (19, 'Basic 5B'),

    (20, 'Basic 6A'),
    (21, 'Basic 6B'),

    (22, 'Basic 7A'),
    (23, 'Basic 7B'),

    (24, 'Basic 8'),
    (25, 'Basic 9'),
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
    is_discounted_student = models.BooleanField(default=False)
    
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
        ('Creche', 'Creche'),

        ('Nursery 1A', 'Nursery 1A'),
        ('Nursery 1B', 'Nursery 1B'),

        ('Nursery 2A', 'Nursery 2A'),
        ('Nursery 2B', 'Nursery 2B'),

        ('KG 1A', 'KG 1A'),
        ('KG 1B', 'KG 1B'),

        ('KG 2A', 'KG 2A'),
        ('KG 2B', 'KG 2B'),

        ('Basic 1A', 'Basic 1A'),
        ('Basic 1B', 'Basic 1B'),

        ('Basic 2A', 'Basic 2A'),
        ('Basic 2B', 'Basic 2B'),

        ('Basic 3A', 'Basic 3A'),
        ('Basic 3B', 'Basic 3B'),

        ('Basic 4A', 'Basic 4A'),
        ('Basic 4B', 'Basic 4B'),

        ('Basic 5A', 'Basic 5A'),
        ('Basic 5B', 'Basic 5B'),

        ('Basic 6A', 'Basic 6A'),
        ('Basic 6B', 'Basic 6B'),

        ('Basic 7A', 'Basic 7A'),
        ('Basic 7B', 'Basic 7B'),

        ('Basic 8', 'Basic 8'),
        ('Basic 9', 'Basic 9'),
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



