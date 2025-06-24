from django.contrib import admin

from api.event.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "generation", "title", "date", "start_time")
    list_filter = ("date", "start_time", "end_time")
    search_fields = ("title", "description")
    list_per_page = 10
