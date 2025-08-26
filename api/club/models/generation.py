from django.db import models

from api.club.models.club import Club
from config.abstract_models.soft_delete_model import SoftDeleteModel


class Generation(SoftDeleteModel):
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
    auto_approve = models.BooleanField(default=False)

    @property
    def member_count(self):
        return self.gen_members.count()
