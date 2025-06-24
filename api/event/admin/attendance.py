from django.contrib import admin

from api.event.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "generation_mapping", "created_at", "status")
    list_filter = ("event", "generation_mapping")
    search_fields = ("event__title", "generation_mapping__member__user__username")
    list_per_page = 10
