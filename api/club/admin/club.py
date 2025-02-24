from django.contrib import admin

from api.club.models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    pass
