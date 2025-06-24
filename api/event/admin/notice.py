from django.contrib import admin

from api.event.models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "title", "created_at")
    list_filter = ("event", "title")
    search_fields = ("title", "content")
    list_per_page = 10
