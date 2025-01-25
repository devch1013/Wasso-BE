from django.contrib import admin

from club.models import GenerationMapping


@admin.register(GenerationMapping)
class UserGenerationAdmin(admin.ModelAdmin):
    pass
