from django.contrib import admin

from club.models import ClubApply


@admin.register(ClubApply)
class ClubApplyAdmin(admin.ModelAdmin):
    pass
