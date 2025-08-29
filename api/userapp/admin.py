from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.html import format_html
from rest_framework_simplejwt.tokens import RefreshToken

from api.userapp.models import User
from api.userapp.models.session import PcSession
from api.userapp.models.version import Version


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "identifier",
        "phone_number",
        "is_staff",
        "is_active",
        "jwt_token_button",
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

    def jwt_token_button(self, obj):
        """JWT 토큰 생성 버튼을 표시하는 메서드"""
        return format_html(
            '<button type="button" onclick="generateJWTToken({})" class="button">JWT 토큰 생성</button>',
            obj.pk,
        )

    jwt_token_button.short_description = "JWT Token"

    def get_urls(self):
        """커스텀 URL을 추가"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate-jwt/<int:user_id>/",
                self.admin_site.admin_view(self.generate_jwt_token),
                name="userapp_user_generate_jwt",
            ),
        ]
        return custom_urls + urls

    def generate_jwt_token(self, request, user_id):
        """JWT 토큰을 생성하고 반환하는 뷰"""
        user = get_object_or_404(User, pk=user_id)

        # RefreshToken을 사용해 토큰 생성 (auth.py의 get_token 메서드와 동일)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return JsonResponse(
            {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "identifier": user.identifier,
                "access_token": str(access_token),
                "refresh_token": str(refresh),
            }
        )

    class Media:
        js = ("admin/js/jwt_token_generator.js",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Version)
admin.site.register(PcSession)
