from django.contrib import admin

from api.generation.models import GenMember


@admin.register(GenMember)
class UserGenerationAdmin(admin.ModelAdmin):
    pass
