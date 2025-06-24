from django.db import models
from django.utils import timezone

from api.club.models.club import Club


class Generation(models.Model):
    def __str__(self):
        return f"{self.club.name} - {self.name}"

    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    activated = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    invite_code = models.CharField(max_length=6, null=True, blank=True)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self):
        self.deleted = True
        self.deleted_at = timezone.localtime(timezone.now())
        self.save()
