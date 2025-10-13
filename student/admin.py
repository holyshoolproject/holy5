from django.contrib import admin
from .models import StudentProfile, GradeClass, AcademicYear, Term, StudentTermRecord, Subject, StudentSubjectRecord

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "contact_of_father",
        "contact_of_mother",
        "has_peculiar_health_issues",
        "name_of_father",
        "name_of_mother",
    )
    list_filter = (
        "class_seeking_admission_to",
        "has_allergies",
        "has_peculiar_health_issues",
    )
    search_fields = (
        "user__full_name",   # assuming your User model has full_name
        "name_of_father",
        "name_of_mother",
    )

@admin.register(GradeClass)
class GradeClassAdmin(admin.ModelAdmin):
    list_display = ("name", "staff")
    list_filter = ("name",)
    search_fields = ("name",)





@admin.register(StudentTermRecord)
class StudentTermRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "get_class", "term", "attendance")
    list_filter = ("term", "grade_class")
    search_fields = ("student__full_name",)

    def get_class(self, obj):
        return obj.grade_class
    get_class.short_description = 'Class'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(StudentSubjectRecord)
class StudentSubjectRecordAdmin(admin.ModelAdmin):
    list_display = ("student_term_record", "subject", "total_score", "grade")
    list_filter = ("subject", "grade")
    search_fields = ("student_term_record__student__full_name", "subject__name")



