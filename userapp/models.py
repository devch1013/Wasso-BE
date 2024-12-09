from django.db import models

class User(models.Model):
    identifier = models.CharField(max_length=255, unique=True, null=True)
    username = models.CharField(max_length=255, unique=True)  # kakao nickname을 username으로 사용
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
