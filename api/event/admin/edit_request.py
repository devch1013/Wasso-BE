from django.contrib import admin

from api.event.models import EditRequest


@admin.register(EditRequest)
class EditRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "gen_member", "created_at", "status")
    list_filter = ("event", "gen_member")
    search_fields = ("event__title", "gen_member__member__user__username")
