from django.contrib import admin

from api.event.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "generation",
        "title",
        "date",
        "start_datetime",
        "end_datetime",
    )
    list_filter = ("date", "start_datetime", "end_datetime")
    search_fields = ("title", "description")
    list_per_page = 10
