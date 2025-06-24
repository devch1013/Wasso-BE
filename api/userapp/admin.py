from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.userapp.models import User


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "identifier",
        "phone_number",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = (
        (None, {"fields": ("username",)}),
        (
            "Personal info",
            {
                "fields": (
                    "email",
                    "identifier",
                    "phone_number",
                    "profile_image",
                    "fcm_token",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email"),
            },
        ),
    )
    search_fields = ("username", "email", "identifier")
    ordering = ("username",)


admin.site.register(User, CustomUserAdmin)
