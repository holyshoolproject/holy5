from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            # Change the label and placeholder
            self.fields['password'].label = 'PIN'
            self.fields['password'].widget.attrs['placeholder'] = 'Enter PIN'
            self.fields['password'].help_text = 'Use a 4-digit PIN for login'


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
        'email',    
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
        ("Personal info", {"fields": ("full_name", "gender", "email", "date_of_birth", "nationality")}),
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
