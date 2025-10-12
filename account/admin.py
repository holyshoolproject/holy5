from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = (
        "user_id",
        "full_name",
        "role",
        "gender",
        "date_of_birth",
        "nationality",
        "is_active",
        "is_staff",
    )

    # Filters in the right sidebar
    list_filter = ("role", "gender", "is_active", "is_staff")

    # Search bar fields
    search_fields = ("user_id", "full_name")

    # Ordering
    ordering = ("user_id",)

    # Fieldsets define how fields appear in the detail form
    fieldsets = (
        (None, {"fields": ("user_id", "password")}),
        ("Personal info", {"fields": ("full_name", "gender", "date_of_birth", "nationality")}),
        ("Role info", {"fields": ("role",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    # Fields required when creating a user via the admin
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user_id", "role", "full_name", "gender", "date_of_birth", "nationality", "password1", "password2"),
            },
        ),
    )
