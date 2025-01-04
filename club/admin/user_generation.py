from django.contrib import admin

from club.models import UserGeneration


@admin.register(UserGeneration)
class UserGenerationAdmin(admin.ModelAdmin):
    pass
