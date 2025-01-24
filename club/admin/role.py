from django.contrib import admin

from club.models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "club"]
