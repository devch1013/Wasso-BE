from django.contrib import admin

from ..models import AbsentApply

@admin.register(AbsentApply)
class AbsentApplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'gen_member', 'created_at', 'status')
    list_filter = ('event', 'gen_member')
    search_fields = ('event__title', 'gen_member__member__user__username')
