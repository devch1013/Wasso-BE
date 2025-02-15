from django.contrib import admin

from api.club.models import ClubApply


@admin.register(ClubApply)
class ClubApplyAdmin(admin.ModelAdmin):
    pass
