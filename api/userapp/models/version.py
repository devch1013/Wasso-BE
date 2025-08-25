from django.db import models

from api.userapp.models.user_meta import Platform


class Version(models.Model):
    version = models.CharField(max_length=255)
    platform = models.CharField(max_length=255, choices=Platform.choices)
    required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "versions"
