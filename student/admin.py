from django.contrib import admin
from .models import StudentProfile, GradeClass, AcademicYear, Term, StudentTermRecord, Subject, StudentSubjectRecord

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "class_seeking_admission_to",
        "has_allergies",
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

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year")
    list_filter = ("name", "academic_year")
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



# fee structure 

from django.contrib import admin
from .models import FeeStructure, StudentFeeRecord, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("academic_year", "grade_class", "term", "amount")
    list_filter = ("academic_year", "grade_class", "term")
    search_fields = ("grade_class__name", "term__name", "academic_year__name")
    ordering = ("academic_year", "grade_class", "term")


@admin.register(StudentFeeRecord)
class StudentFeeRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "fee_structure", "amount_paid", "balance", "is_fully_paid")
    list_filter = ("fee_structure__academic_year", "fee_structure__term", "is_fully_paid")
    search_fields = ("student__user__full_name", "fee_structure__grade_class__name")
    ordering = ("student",)
    readonly_fields = ("balance", "is_fully_paid")  # so admin can’t edit these manually


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student_fee_record", "date", "amount", "payment_method", "reference")
    list_filter = ("payment_method", "date")
    search_fields = (
        "student_fee_record__student__user__full_name",
        "reference",
    )
    ordering = ("-date",)
