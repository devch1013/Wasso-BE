from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    identifier = models.CharField(max_length=255, unique=True, null=True)
    username = models.CharField(max_length=255, unique=True)  # kakao nickname을 username으로 사용
    
    # username field를 kakao nickname으로 사용할 것이므로 email을 필수값에서 제외
    email = models.EmailField(blank=True, null=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ["identifier"]  # email을 필수값에서 제외
    
    # Add related_name to avoid clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    class Meta:
        db_table = 'users'
