from django.contrib import admin

from api.club.models import GenMember


@admin.register(GenMember)
class UserGenerationAdmin(admin.ModelAdmin):
    pass
