from django.contrib import admin

from api.generation.models import Generation


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "club", "activated"]
