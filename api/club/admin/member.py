from django.contrib import admin

from api.club.models import Member


@admin.register(Member)
class UserClubAdmin(admin.ModelAdmin):
    pass
