from django.contrib import admin
from .models import Family, FamilyFeeRecord, FamilyPayment


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "get_members")
    search_fields = ("name", "members__full_name")

    def get_members(self, obj):
        return ", ".join(user.full_name for user in obj.members.all())
    get_members.short_description = "Family Members"


@admin.register(FamilyFeeRecord)
class FamilyFeeRecordAdmin(admin.ModelAdmin):
    list_display = ("family", "term", "academic_year", "amount_to_pay", "amount_paid", "balance", "is_fully_paid", "date_created")
    list_filter = ("term", "academic_year")
    search_fields = ("family__name", "family__members__full_name")
    readonly_fields = ("balance",)
    ordering = ("-date_created",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("family", "term", "academic_year")


@admin.register(FamilyPayment)
class FamilyPaymentAdmin(admin.ModelAdmin):
    list_display = ("family_fee_record", "amount", "payment_method", "date")
    list_filter = ("payment_method", "date")
    search_fields = (
        "family_fee_record__family__name",
        "family_fee_record__family__members__full_name",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("family_fee_record", "family_fee_record__family")
