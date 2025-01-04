from django.contrib import admin

from club.models import UserClub


@admin.register(UserClub)
class UserClubAdmin(admin.ModelAdmin):
    pass
