from django.contrib import admin

from api.event.models import Abusing


@admin.register(Abusing)
class AbusingAdmin(admin.ModelAdmin):
    list_display = ("id", "attendance", "reason", "created_at")
    list_filter = ("attendance",)
    search_fields = ("reason",)
