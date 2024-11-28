from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # identifier 필드를 list_display에 추가
    list_display = ('username', 'identifier', 'email', 'first_name', 'last_name', 'is_staff')
    
    # identifier 필드를 fieldsets에 추가
    fieldsets = (
        (None, {'fields': ('username', 'identifier', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                  'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # identifier 필드를 add_fieldsets에 추가 (유저 생성 시 보이는 필드들)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'identifier', 'password1', 'password2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
