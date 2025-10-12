from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from .models import FeeStructure, StudentFeeRecord, Payment



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
    list_display = ("student", "fee_structure", "amount_paid", "balance", "is_fully_paid")
    list_filter = ("fee_structure__academic_year", "fee_structure__term", "is_fully_paid")
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

