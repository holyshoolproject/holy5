from django.contrib import admin
from .models import StaffProfile

# Register your models here.
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__full_name",)