from django.contrib import admin

from api.club.models import GenerationMapping


@admin.register(GenerationMapping)
class UserGenerationAdmin(admin.ModelAdmin):
    pass
