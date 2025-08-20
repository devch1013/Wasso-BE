from django.contrib import admin

from api.generation.models import ClubApply


@admin.register(ClubApply)
class ClubApplyAdmin(admin.ModelAdmin):
    pass
