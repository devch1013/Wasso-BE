from django.contrib import admin

from club.models import Member


@admin.register(Member)
class UserClubAdmin(admin.ModelAdmin):
    pass
