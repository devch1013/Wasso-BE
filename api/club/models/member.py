from django.contrib.postgres.fields import ArrayField
from django.db import models

from api.club.models.club import Club
from api.userapp.models import User


class Member(models.Model):
    def __str__(self):
        return f"{self.user.username} - {self.club.name}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="members")
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = ArrayField(
        models.CharField(max_length=100), blank=True, null=True, default=list
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_current_generation(self):
        return self.genmember_set.filter(is_current=True).first()

    class Meta:
        db_table = "member"
