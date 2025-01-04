from django.contrib.auth.models import AbstractUser
from django.db import models

# Add this custom UserManager


class User(AbstractUser):
    identifier = models.CharField(max_length=255, unique=True, null=True)
    username = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.URLField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "identifier"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
