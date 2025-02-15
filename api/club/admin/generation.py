from django.contrib import admin

from api.club.models import Generation


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "club"]
