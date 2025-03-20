from django.contrib import admin

from ..models import AbsentApply

@admin.register(AbsentApply)
class AbsentApplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'created_at', 'status')
    list_filter = ('event', 'user')
    search_fields = ('event__title', 'user__username')
