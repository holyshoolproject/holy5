from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from .models import FeeStructure, StudentFeeRecord, Payment, AcademicYear, Term, GradeClass



@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year")
    list_filter = ("name", "academic_year")
    search_fields = ("name",)



# Fee Structure admin
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("academic_year", "grade_class", "term", "amount")
    list_filter = ("academic_year", "grade_class", "term")
    search_fields = ("grade_class__name", "term__name", "academic_year__name")
    ordering = ("academic_year", "grade_class", "term")


# Student Fee Record admin
@admin.register(StudentFeeRecord)
class StudentFeeRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "fee_structure", "amount_paid", "balance", "is_fully_paid", "date_created")
    list_filter = ("student__current_class", "is_fully_paid", "fee_structure")
    search_fields = ("student__user__full_name", "fee_structure__grade_class__name")
    ordering = ("student",)
    readonly_fields = ("balance", "is_fully_paid")


# Payment admin (with improved raw_id widget)
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student_fee_record", "date", "amount", "payment_method", )
    list_filter = ("payment_method", "date")
    search_fields = ("student_fee_record__student__user__full_name",)
    ordering = ("-date",)
    autocomplete_fields = ["student_fee_record"]  # Use this instead of raw_id_fields

